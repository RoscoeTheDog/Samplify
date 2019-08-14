import os
import time
import glob
import sys
import pydub as pd
import io
import multiprocessing
import threading

# important paths
input_path = 'C:/Users/Admin/Desktop/Input'
output_path = 'C:/Users/Admin/Desktop/Output'
database_path = 'C:/Users/Admin/Google Drive/1. Software Engineering/Python/Samplify/database/database.db'

# check to see what computer we're on
if not os.path.exists(database_path):
    input_path = 'C:/Users/Aspen/Desktop/Input'
    output_path = 'C:/Users/Aspen/Desktop/Output'
    database_path = 'C:/Users/Aspen/Google Drive/1. Software Engineering/Python/Samplify/database/database.db'

thread_event1 = threading.Event()
thread_event2 = threading.Event()

num_threads = 1

master_thread_list = list

exclusions = []
exclusion_set = []
exclusion_iter = 0

keywords = []
keyword_iter = 0

input_path_contents = []

ext_type = '.wav'
conv_type = 'wav'
bit_depth = 3  # 1-4. 1=8 2=16 3=24 4=32
target_dbfs = -24

thread_lock = threading.Lock()

verbose_timer = 0
file_check_timer = .22


def get_keywords():

    while True:



        # PROMPT FOR KEYWORD INPUT
        new_word = input('New Keyword: ')

        # CHECK IF KEYWORD ALREADY EXISTS
        if new_word in keywords:
            print('Keyword already exists')

        # ADD KEYWORD TO LIST IF DOESN'T
        if new_word != '':  # (RETURNS FALSE)
            keywords.append(new_word)
            print(keywords)
            print()
            global exclusion_set
            exclusion_set = []
            get_exclusions(new_word)  # CALL GET_EXCLUSIONS FUNCTION
            print()

        # IF 'DONE', CONFIRM?
        else:
            confirm_prompt = "Please Confirm Settings"
            print()
            while confirm_prompt != 'Please Confirm Settings...':
                confirm_prompt = confirm_prompt + '.'
                sys.stdout.write('\r' + confirm_prompt)
                time.sleep(.25)
            print()
            print()
            print(keywords)
            print()
            print(exclusions)

            print()
            confirmation = input('Confirm?(y/n) ')
            if confirmation == 'n':
                keywords.clear()
                exclusions.clear()
            if confirmation == 'y':
                break

def get_exclusions(new_word):
    global exclusion_set
    global exclusion_iter
    global keyword_iter

    # ASK FOR ANY EXCLUSIONS AFTER ADDING KEYWORD
    while True:
        new_exclusion = input(f'New Exclusion For \'{new_word}\':')

        if new_exclusion != '':
            # CHECK IF EXCLUSION ALREADY EXISTS
            if new_exclusion in exclusion_set:
                print()
                print(f'Exclusion Already Added: \'{new_exclusion}\'')
                print()
            # ADD TO LIST IF NOT
            else:
                exclusion_set.append(new_exclusion)
                print(exclusion_set)
                exclusion_iter = exclusion_iter + 1
                print()

        # BREAK LOOP IF NOT
        else:
            if len(exclusion_set) < 1:
                print()
                print('No Exclusions Entered ')
                break

            exclusions.append(exclusion_set)
            print(exclusions)
            keyword_iter = keyword_iter + 1
            break


def create_input():

    # Create Input Folder on Desktop
    input_directory = os.path.dirname(input_path)
    os.chdir(input_path)
    # Check to see if exists
    if not os.path.exists(input_directory):
        os.makedirs(input_directory)


def create_output():

    # CHANGE DIRECTORY
    os.chdir(output_path)

    # CREATE OUTPUT DIR
    if not os.path.exists(output_path):
        os.makedirs(output_path)


def get_files():
    global input_path
    global input_path_contents
    global ext_type
    global basename_no_extension
    global q

    # SELECT INPUT DIR
    os.chdir(input_path)

    iterator = 0
    iterator2 = 0

    for r, d, f in os.walk(input_path):
        for i in glob.glob(r + '**/*' + ext_type):
            if not False:
                input_path_contents.append(i)
                #q.put(i)
                iterator = iterator + 1

    # FILTER OUT PATH AND EXTENSION TYPE 'justname'
    for file in input_path_contents:
        _basename = os.path.basename(file)

        # TAKE OUT THE EXTENSION TYPE OF NAME
        if _basename.endswith(ext_type):
            _basename = _basename[:-len(ext_type)]
            basename_no_extension.append(_basename)
            iterator2 = iterator2 + 1

    print(iterator)
    print(iterator2)


def task_service():
    global input_path_contents
    global next_basename
    global master_thread_list
    global thread_lock
    global thread_event1
    global thread_event2
    global output_path_contents_basename
    global output_path_contents

    while True:

        thread_event1.wait()

        print('searching for new files!')
        print()
        time.sleep(verbose_timer)

        input_path_contents = []

        # CHECK FOR FILES WITH KEYWORDS
        for r, d, f in os.walk(input_path):
            for check_path in glob.glob(r + '**/*' + ext_type):
                if check_path not in input_path_contents:
                    for word in keywords:
                        if word.casefold() in os.path.basename(check_path.casefold()):
                            print('file found: ', check_path)
                            input_path_contents.append(check_path)

        # CHECK FOR FILES WITH EXCLUSION WORDS
        for word in keywords:
            for file in input_path_contents:
                for _exc_set in exclusions:
                    for exc in _exc_set:
                        if word.casefold() in file.casefold():
                            if exc.casefold() in file.casefold():
                                print('file excluded: ', file)
                                input_path_contents.remove(file)

        print()

        # MAKE A BASENAME LIST TO X CHECK INS AND OUTS
        input_path_contents_basename = []

        for path in input_path_contents:
            basename = os.path.basename(path)
            if basename.endswith(ext_type):
                basename = basename[:-len(ext_type)]
                input_path_contents_basename.append(basename)

        """
            we need to perform a scan of the output directory and
            get the basename so we can verify if the file has already
            been processed.
        """

        output_path_contents = []

        for r, d, f in os.walk(output_path):
            for check_path in glob.glob(r + '**/*' + ext_type):
                if check_path not in output_path_contents:
                    output_path_contents.append(check_path)

        output_path_contents_basename = []

        for file in output_path_contents:
            basename = os.path.basename(file)
            if basename.endswith(ext_type):
                basename = basename[:-len(ext_type)]
                output_path_contents_basename.append(basename)

        """ 
            and we will also need to perform our sync check
            before updating and calling threads for tasking
        """

        # ARE BOTH DIRECTORIES SYNCED?
        for in_basename in input_path_contents_basename:
            if in_basename in output_path_contents_basename:
                print('input & output directories synchronized')
                print()

        # IF NOT, UPDATE OUR THREADS
            else:
                master_thread_list = [[] for x in range(num_threads)]

                """
                we need to create a way to transfer files efficiently to our threads
                so we will duplicate our input list, distribute each item, and remove it from the list as we go
                """

                distribute_contents = input_path_contents.copy()

                while len(distribute_contents) > 0:
                    for i in range(num_threads):
                        if len(distribute_contents) == 0:
                            break

                        removed = distribute_contents.pop()  # we can declare pop for debugging
                        master_thread_list[i].append(removed)

                master_file_count = 0
                for thread in master_thread_list:
                    for f in thread:
                        master_file_count = master_file_count + 1
                print('number of files: ', master_file_count)
                print()
                time.sleep(verbose_timer)

                """
                    finally, lets clear this event and go to the next.
                """

                thread_event1.clear()
                print('cleared event1')
                print()
                time.sleep(verbose_timer)

                thread_event2.set()
                print('setting event2')
                print()
                time.sleep(verbose_timer)


def get_basename(file_path):
    global basename_no_extension
    global input_path_contents

    # FILTER OUT PATH AND EXTENSION TYPE 'justname'
    _basename = os.path.basename(file_path)

    # TAKE OUT THE EXTENSION TYPE OF NAME
    if _basename.endswith(ext_type):
        _basename = _basename[:-len(ext_type)]
        basename_no_extension.append(_basename)


def set_bit_depth(audio):
    global bit_depth

    print('INPUT BIT-DEPTH: ', audio.sample_width)

    # CHECK TO SEE IF BIT-DEPTH IS GREATER THAN SPECIFIED BIT-DEPTH
    if audio.sample_width > bit_depth:
        print('CHANGING TO 24 OR HIGHER...')
        audio = audio.set_sample_width(bit_depth)

    # IF 8 BIT CHANGE TO MINIMUM 16
    elif audio.sample_width == 1:
        audio = audio.set_sample_width(2)

    else:
        print('BIT-DEPTH LOWER THAN TARGET, SKIPPING...')

    print('OUTPUT BIT-DEPTH: ', audio.sample_width)
    print()
    return audio


def set_mono(audio):

    audio = audio.set_channels(1)
    print('CONVERTING TO MONO ')
    print()
    return audio


# def normalize_peak():
#
#     iterator = 0
#
#     for file in basename_no_extension:
#
#         # (THIS IS TO MAKE THE EXPORT SYNTAX MORE READABLE)
#         converted_output = output_path + '\\' + file + '.' + conv_type
#
#         # OPEN FILE
#         audio = pd.AudioSegment.from_file(input_path_contents[iterator])
#
#         # SET OUR BITDEPTH
#         print('INPUT BIT-DEPTH', audio.sample_width)
#         #set_bit_depth()
#         print('OUTPUT BIT-DEPTH ', audio.sample_width)
#
#         # FILE'S PEAK DBFS (-)
#         peak_amplitude = audio.max_dBFS
#         print('CLIP PEAK dBFS: ', peak_amplitude)
#
#         applied_gain = peak_amplitude - 0.3
#
#         # APPLY THE MAX PEAK POSSIBLE WITH (-0.3 CLIP PREVENTION)
#         audio = audio.apply_gain(peak_amplitude - 0.3)
#
#         print('APPLIED dBFS: ', applied_gain)
#
#         # CONVERT, NAME AND EXPORT AUDIO FILE
#         audio.export(converted_output, format=conv_type)
#
#         # PRINT THE OUTPUT
#         print('exported ', converted_output)
#         print()
#
#         # GO TO NEXT FILE
#         iterator = iterator + 1


def normalize_rms(audio):
    global target_dbfs
    global input_path_contents

    # FILE'S AVERAGE RMS dBFS (-)
    loudness_db = audio.dBFS

    # CHECK TO SEE IF CLIPPED
    if loudness_db > 0:
        loudness_db = 0
    print('AVERAGE VOLUME (RMS): ', loudness_db)

    # FIND THE DIFFERENCE FROM CURRENT DB TO TARGET
    change_in_dbfs = target_dbfs - loudness_db
    print('TRYING TO APPLY: ', change_in_dbfs)

    # FIND AUDIO'S PEAK DBFS (-)
    peak_amplitude = audio.max_dBFS
    print('CLIP PEAK VOLUME: ', peak_amplitude)

    # FIND THE TARGET'S TOTAL CEILING VALUE
    current_ceiling = peak_amplitude + change_in_dbfs
    print('CLIP PEAK POST VOLUME: ', current_ceiling)

    # NORMALIZATION CLIP PREVENTION
    if current_ceiling > 0.00:  # IF CEILING VALUE IS LARGER THAN 0
        audio = audio.apply_gain(change_in_dbfs + -current_ceiling - 0.03)  # REDUCE
        print('CLIPPING DETECTED, LOWERING: ', -current_ceiling)

    else:  # OTHERWISE, NORMALIZE TO TARGET RMS
        audio = audio.apply_gain(change_in_dbfs)

    print('ACHIEVED RMS VALUE (dBFS) ', audio.dBFS)
    print()

    return audio


def open_audio(file_path):
    # OPEN FILE
    print('OPEN FILE: ', file_path)
    print()
    audio = pd.AudioSegment.from_file(file_path)
    return audio


def export(file_path, audio):
    global basename_no_extension

    # FILTER OUT PATH AND EXTENSION TYPE 'justfilename'
    _basename = os.path.basename(file_path)

    # TAKE OUT THE EXTENSION TYPE OF NAME
    if _basename.endswith(ext_type):
        _basename = _basename[:-len(ext_type)]

    for words in keywords:
        # CREATE SUBDIRECTORIES BASED ON KEYWORDS
        if not os.path.exists(words):
            os.mkdir(words)

        # GATHER SUBDIRECTORIES
        sub_directories = next(os.walk(output_path))[1]
        if words.casefold() in file_path.casefold():

            # NEST IN SUBDIRECTORIES
            for directories in sub_directories:
                if directories.casefold() in file_path.casefold():
                    converted_output = directories + '\\' + _basename + '.' + conv_type
                    audio.export(converted_output, format=conv_type)

                    print('EXPORTED: ', file_path)
                    print()

                    return file_path


def thread_task(num):
    global thread_lock
    global thread_event1
    global thread_event2

    counter = 0

    while True:
        thread_event2.wait()

        print('processing next file ', counter)
        print()
        time.sleep(verbose_timer)

        nest_list = master_thread_list[num]

        """ 
        we need to make a way to see if the file being used
        has already been exported in the output folder.
        
        so we'll check by the input basename (without any path or extension, for accuracy)
        """

        scan_file = 0

        for file_path in nest_list:

            basename = os.path.basename(file_path)

            if basename.endswith(ext_type):
                input_basename = basename[:-len(ext_type)]

                # HAS THE FILE BEEN DONE ALREADY?

                print('checking file status... ')
                print('filename: ', file_path)
                print('scan number: ', scan_file)
                print()
                time.sleep(file_check_timer)

                if input_basename in output_path_contents_basename:
                    scan_file = scan_file + 1
                    continue

                elif input_basename not in output_path_contents_basename:

                    """
                    this is where we will actually start calling functions to convert with
                    """

                    # 'TRY' JUST IN CASE PATH WAS FORCEFULLY REMOVED SOMEHOW
                    try:
                        print('**********************')
                        print()
                        print('WORKING THREAD: ', num)
                        print()
                        print('WORKING LIST: ', nest_list)
                        print()
                        print('WORKING FILE: ', file_path)
                        print()
                        print('WORKING BASENAME: ', basename)
                        print()

                        audio = open_audio(file_path)

                        audio = set_mono(audio)

                        audio = set_bit_depth(audio)

                        audio = normalize_rms(audio)

                        export(file_path, audio)

                        counter = counter + 1

                        time.sleep(verbose_timer)

                    # AVOID CRASH IN WORST CASE SCENARIO
                    except:
                        print('FILE CANNOT BE OPENED. POSSIBLE FILE PATH MISSING?')
                        print()
                        time.sleep(verbose_timer)

                    finally:
                        thread_event2.clear()
                        print('clearing event2...')
                        print()
                        time.sleep(verbose_timer)

                        thread_event1.set()
                        print('setting event1...')
                        print()
                        time.sleep(verbose_timer)

                        break

        thread_event2.clear()
        print('clearing event2...')
        print()
        time.sleep(verbose_timer)

        thread_event1.set()
        print('setting event1...')
        print()
        time.sleep(verbose_timer)


def threads():

    # START TASK_SERVICE THREAD
    p = threading.Thread(target=task_service)
    p.isDaemon()
    p.start()
    thread_event1.set()

    # SMALL BREAK TO ALLOW LIST TO GATHER UPON STARTUP
    #time.sleep(.25)

    thread_list = []

    # START MULTI-THREADED CONVERSION
    for num in range(num_threads):
        p2 = threading.Thread(target=thread_task, args=(num,))
        p2.isDaemon()
        p2.start()
        thread_list.append(p2)

    # JOIN THREADS IF NOT CONTINUOUS
    # for thread in thread_list:
    #     thread.join()
    #
    # p.join()


def main():

    create_input()

    create_output()

    get_keywords()

    #timestart = time.time()  # START OUR TIMER

    threads()

    #print(time.time() - timestart)


if __name__ == '__main__':
    main()