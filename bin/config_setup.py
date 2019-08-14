import os
import settings


def template_write():

    # PROMPT FOR TEMPLATE NAME
    template_new = input('Set New Template Name: ')
    print(template_new)
    print()

    while True:
        new_parent = input('New Parent Folder: ')
        new_parent_path = settings.output_path + '/' + new_parent
        for r, d, f in os.walk(settings.output_path):
            if new_parent in d:
                print('Parent Folder Already Exists')
                print()
                break
            elif new_parent is '':
                print('that is the default directory! Ending New Parent Entry...')
                print()
                break
            elif not os.path.exists(new_parent_path):
                os.mkdir(new_parent_path)

                while True:
                    new_child = input('New Child Folder For ' + new_parent)
                    new_child_path = new_parent_path + '/' + new_child
                    print(new_child_path)
                    print()

                    if new_child == '':
                        break

                    if not os.path.exists(new_child_path):
                        os.mkdir(new_child_path)

                    while True:
                        new_sub_child = input('New Child Folder For: ' + new_child)
                        new_sub_child_path = new_child_path + '/' + new_sub_child
                        print(new_sub_child_path)
                        print()

                        if not os.path.exists(new_sub_child_path):
                            os.mkdir(new_sub_child_path)

                        elif new_sub_child == '':
                            break
        if new_parent == '':
            break

    return template_new