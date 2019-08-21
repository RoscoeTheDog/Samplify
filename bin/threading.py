import settings
import samplify.pd_functions as pd_func

import time
import os
import glob
import threading
import console
import logging

# declare our event triggers for managing seperate threads
event_scan = threading.Event()
event_process = threading.Event()

# declare our interfaces from console module
printUser = console.logging.printUser
printDebug = console.logging.printDebug

logger = logging.getLogger("main")


def task_service():

    while True:
        event_scan.wait()
        printDebug('event_scan unlocked')
        printDebug('')
        printDebug('fetching paths from root input')
        time.sleep(settings.debug_timer)

        # redeclare list to update root folder contents-- including removed files
        settings.input_path_contents = []

        # gather all qualified files
        for r, d, f in os.walk(settings.input_path):
            for check_path in glob.glob(r + '**/*' + settings.ext_type):
                if check_path not in settings.input_path_contents:
                    for word in settings.keywords:
                        if word.casefold() in os.path.basename(check_path.casefold()):
                            print('file found: ' + check_path)
                            settings.input_path_contents.append(check_path)
        print()

        # reference to keyword list and remove any files from path list
        printDebug('removing paths with exclusions')
        time.sleep(settings.debug_timer)

        for word in settings.keywords:
            for file in settings.input_path_contents:
                for _exc_set in settings.exclusions:
                    for exc in _exc_set:
                        if word.casefold() in file.casefold():
                            if exc.casefold() in file.casefold():
                                print('file excluded: ' + file)
                                settings.input_path_contents.remove(file)

        print()

        printDebug('getting names from input paths')

        settings.input_path_contents_basename = []

        for path in settings.input_path_contents:
            basename = os.path.basename(path)
            if basename.endswith(settings.ext_type):
                basename = basename[:-len(settings.ext_type)]  # split (:) negative (-) length(ext_type)
                settings.input_path_contents_basename.append(basename)

        """
            we need to perform a scan of the output directory and
            get the basename so we can verify if the file has already
            been processed.
        """

        settings.output_path_contents = []

        for r, d, f in os.walk(settings.output_path):
            for check_path in glob.glob(r + '**/*' + settings.ext_type):
                if check_path not in settings.output_path_contents:
                    settings.output_path_contents.append(check_path)

        printDebug('getting names from output paths')

        settings.output_path_contents_basename = []

        for file in settings.output_path_contents:
            basename = os.path.basename(file)
            if basename.endswith(settings.ext_type):
                basename = basename[:-len(settings.ext_type)]
                settings.output_path_contents_basename.append(basename)

        printDebug('checking for completed files in output')
        printDebug('')

        # REMOVE COMPLETED FILES FROM QUEUE

        distribute_contents = settings.input_path_contents.copy()

        scan = 0
        while scan < len(distribute_contents):
            printDebug('scan #: ' + scan)
            printDebug('length to scan: ' + str(len(distribute_contents)))

            # get filename from path
            filename = os.path.basename(distribute_contents[scan])[:-len(settings.ext_type)]

            printDebug('checking name: ' + filename)
            printDebug(settings.output_path_contents_basename)
            printDebug(distribute_contents)
            time.sleep(settings.debug_timer)

            if filename in settings.output_path_contents_basename:
                printDebug('file complete. removed: ' + distribute_contents[scan])
                printDebug('')
                distribute_contents.remove(distribute_contents[scan])
                if not scan == 0:
                    scan = scan - 1

            else:
                printDebug('file accepted')
                printDebug('')
                scan = scan + 1

        printDebug('check complete')
        time.sleep(settings.debug_timer)

        """
        we need to create a way to feed files efficiently into our conversion threads.
        so we will duplicate our input list, distribute each item separately and remove it as we go
        """

        settings.master_thread_list = [[] for x in range(settings.num_threads)]

        # distribute_contents = settings.input_path_contents.copy()

        printDebug('sorting files to threads')
        time.sleep(settings.debug_timer)
        while len(distribute_contents) > 0:
            for i in range(settings.num_threads):
                if len(distribute_contents) == 0:
                    break
                removed = distribute_contents.pop()
                settings.master_thread_list[i].append(removed)

        printDebug('files sorted')
        time.sleep(settings.debug_timer)
        printDebug('')

        # printDebug('collecting file count')
        # master_file_count = 0
        #
        # for thread in settings.master_thread_list:
        #     for f in thread:
        #         master_file_count = master_file_count + 1
        #
        # print('number of total files: ', master_file_count)
        # print()
        # time.sleep(settings.debug_timer)

        printDebug('clearing event_scan')
        time.sleep(settings.debug_timer)
        event_scan.clear()

        printUser('setting event_process')
        time.sleep(settings.debug_timer)
        event_process.set()
        # break

        # # are both directories synced (any work to do)?
        # for in_basename in settings.input_path_contents_basename:
        #     printDebug('working name: ' + in_basename)
        #
        #     if settings.input_path_contents_basename == settings.output_path_contents_basename:
        #         # printDebug('I/O synchronized')
        #         # time.sleep(settings.debug_timer)
        #         pass
        #
        #     else:
        #         printDebug('I/O detected unequal')
        #         time.sleep(settings.debug_timer)
        #
        #         """
        #         we need to create a way to feed files efficiently into our conversion threads.
        #         so we will duplicate our input list, distribute each item separately and remove it as we go
        #         """
        #
        #         settings.master_thread_list = [[] for x in range(settings.num_threads)]
        #
        #         # distribute_contents = settings.input_path_contents.copy()
        #
        #         printDebug('sorting paths to threads lists')
        #         printDebug('')
        #         while len(distribute_contents) > 0:
        #             for i in range(settings.num_threads):
        #                 if len(distribute_contents) == 0:
        #                     break
        #                 removed = distribute_contents.pop()
        #                 settings.master_thread_list[i].append(removed)  # sorted thread list
        #
        #         printDebug('collecting file count')
        #         printDebug('')
        #         master_file_count = 0
        #
        #         for thread in settings.master_thread_list:
        #             for f in thread:
        #                 master_file_count = master_file_count + 1
        #         print('number of files: ', master_file_count)
        #         time.sleep(settings.debug_timer)
        #
        #         printDebug('clearing event_scan')
        #         time.sleep(settings.debug_timer)
        #         event_scan.clear()
        #
        #         printUser('setting event_process')
        #         time.sleep(settings.debug_timer)
        #         event_process.set()
        #         break


def thread_task(num):
    global event_scan
    global event_process

    while True:
        event_process.wait()
        printDebug('event_process unlocked')
        time.sleep(settings.debug_timer)

        scan_counter = 0

        printDebug(['processing next file ', scan_counter])
        time.sleep(settings.debug_timer)

        thread_queue = settings.master_thread_list[num]

        """ 
        we need to check if the file being used has already been exported in the output folder,
        similar to how we synced the task service
        """

        for file_path in thread_queue:
            basename = os.path.basename(file_path)

            if basename.endswith(settings.ext_type):
                input_basename = basename[:-len(settings.ext_type)]  # split (:) negative (-) length(ext_type)

                # printDebug('checking file status')
                # print('scan number: ', scan_counter)

                # REMOVED SINCE WE CHECK AT SCAN STAGE

                # if input_basename in settings.output_path_contents_basename:
                #     printDebug('FILE ' + file_path + ' ALREADY IN OUTPUT, SKIPPING')
                #     scan_counter = scan_counter + 1
                #     time.sleep(settings.file_check_timer)
                #     continue

                #elif input_basename not in settings.output_path_contents_basename:


                # printDebug('')
                # printDebug('file not completed! initializing conversion')

                # 'TRY' JUST IN CASE SOMETHING GOES WRONG
                try:
                    print('**********************')
                    print()
                    print('WORKING THREAD: ', num)
                    print()
                    print('WORKING LIST: ', thread_queue)
                    print()
                    print('WORKING FILE: ', file_path)
                    print()
                    print('WORKING BASENAME: ', basename)
                    print()

                    audio = pd_func.open_audio(file_path)

                    audio = pd_func.set_mono(audio)

                    audio = pd_func.set_bit_depth(audio)

                    audio = pd_func.normalize_rms(audio)

                    pd_func.export(file_path, audio)

                    time.sleep(settings.debug_timer)

                # EXCEPT ANY WORST CASE SCENARIO
                except:
                    printDebug('exception thrown! possible file path missing?')
                    printDebug('')
                    time.sleep(settings.debug_timer)

                finally:
                    printDebug('event_process cleared')
                    time.sleep(settings.debug_timer)
                    event_process.clear()

                    printDebug('event_scan set')
                    time.sleep(settings.debug_timer)
                    event_scan.set()

                    break
        if len(thread_queue) == 0:
            isFinished = True
        # catch the event and end if no files in thread_queue
        if len(thread_queue) == 0:
            printDebug('status complete')
            printDebug('clearing event_process')
            printDebug('')
            time.sleep(settings.debug_timer)
            event_process.clear()

            printDebug('setting event_scan')
            printDebug('')
            time.sleep(settings.debug_timer)
            event_scan.set()


def start_threads():

    # START TASK_SERVICE THREAD
    p = threading.Thread(target=task_service)
    p.isDaemon()
    p.start()
    event_scan.set()  # release scan thread from initial blocking

    # START MULTI-THREADED CONVERSION
    for num in range(settings.num_threads):
        p2 = threading.Thread(target=thread_task, args=(num,))
        p2.isDaemon()
        p2.start()
        settings.thread_exec_instances.append(p2)

    # #JOIN THREADS IF NOT CONTINUOUS
    #
    # for thread in settings.thread_exec_instances:
    #     thread.join()

    #p.join()