import inspect
import re
import asyncio


class ComputeRules(object):

    def __init__(self, file, directory):
        self.input_directory = file
        self.output_directories = {}
        self.rules = {}
        self.file = file
        self.directory = directory

    def __call__(self):
        self.something = create_instance()


    def call_everything(self):
        attributes = (getattr(self.something.call_test, name) for name in dir(self.something.call_test) if not name.startswith('__'))
        class_methods = filter(inspect.ismethod, attributes)

        for rule in class_methods:
            rule()

    def print_stuff(self):
        print(self.file)
        print(self.directory)


@ComputeRules
def create_instance():
    call_test = ComputeRules('c://test ', "c://Please work.")
    return call_test

# attributes = (getattr(call_test, name) for name in dir(call_test) if not name.startswith('__'))
# class_methods = filter(inspect.ismethod, attributes)
#
# for rule in class_methods:
#     rule()


call_test.call_everything()

        # task_list = []
        # for rule in class_methods:
        #     task_list.append(asyncio.create_task(rule()))
        #
        # for t in task_list:
        #     await t

        # del (self.rules)
        # del (self.files)
        # del (self.directory)
        # return vars(ComputeRules)

    # async def contains_expression(self):
    #     exp = self.directory.get('expression')
    #     if exp:
    #         pattern = re.compile(exp)
    #         search = pattern.finditer(self.file.file_name)
    #         for match in search:
    #             self.output_directories[self.file.file_path] = self.directory.path

    # def created_between(self, file, directory):
    #     created_before = directory.get('createdBefore')
    #     created_after = directory.get('createdAfter')
    #
    #     # TODO: check date-time and validate.
    #
    # def contains_extension(self, file, directory):
    #     has_extension = directory.get('hasExtension')
    #     for extension in has_extension.split(','):
    #         if file.extension.lower() in extension.lower():
    #             return True
    #     return False
    #
    # def has_video_stream(self, file, directory):
    #     has_video = directory.get('hasVideo')
    #     if has_video == 'True':
    #         if file.v_stream:
    #             return True
    #     return False
    #
    # def has_audio_stream(self, file, directory):
    #     has_audio = directory.get('hasAudio')
    #     if has_audio == 'True':
    #         if file.a_stream:
    #             return True
    #     return False
    #
    # def has_image_stream(self, file, directory):
    #     has_image = directory.get('hasImage')
    #     if has_image == 'True':
    #         if file.i_stream:
    #             return True
    #     return False


# test_file = ComputeRules('c:/test/', 'c:/output/')
# print(vars(test_file))