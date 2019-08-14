import settings
import sys
import time


def get_keywords():
    global exclusion_set  # access for re-declaration after each call to exclusions()

    while True:
        new_word = input('New Keyword: ')

        # does keyword already exist?
        if new_word in settings.keywords:
            print('Keyword Already Exists')

        # if not, add!
        elif new_word != '':  # (RETURNS FALSE)
            settings.keywords.append(new_word)
            print(settings.keywords)
            print()

            exclusion_set = []
            get_exclusions(new_word)  # CALL GET_EXCLUSIONS FUNCTION

            print()

        # if done, confirm.
        else:
            confirm_prompt = "Please Confirm Settings"
            print()
            while confirm_prompt != 'Please Confirm Settings...':
                confirm_prompt = confirm_prompt + '.'
                sys.stdout.write('\r' + confirm_prompt)
                time.sleep(.25)
            print()
            print()
            print(settings.keywords)
            print()
            print(settings.exclusions)

            print()
            confirmation = input('Confirm?(y/n) ')
            if confirmation == 'n':
                settings.keywords.clear()
                settings.exclusions.clear()
            if confirmation == 'y':
                break


def get_exclusions(new_word):
    global exclusion_set  # access to append entries before re-declaration on next iteration

    # enter a new exclusion for keyword
    while True:
        new_exclusion = input(f'New Exclusion For \'{new_word}\':')

        if new_exclusion != '':
            # does exclusion already exist?
            if new_exclusion in exclusion_set:
                print()
                print(f'Exclusion Already Added: \'{new_exclusion}\'')
                print()
            # if not, add!
            else:
                exclusion_set.append(new_exclusion)  # append each individual exclusion
                print(exclusion_set)
                print()

        # if none entered, exit.
        else:
            if len(exclusion_set) == 0:
                print()
                print('No Exclusions Entered ')
                break

            settings.exclusions.append(exclusion_set)  # append all exclusions for this keyword to a master list
            print(settings.exclusions)
            print()
            break