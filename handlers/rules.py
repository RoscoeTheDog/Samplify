import re
import inspect
import itertools

class ComputeRules(object):

    def __init__(self, file, directory):
        # These will be what is callable from vars(class instance)
        self.input_directory = file.file_path
        self.output_directories = {}

        # These will be what is removed from memory after calling cleanup() method.
        self.rules = {}
        self.file = file
        self.directory = directory

    def __delattr__(self, item):
        super().__delattr__(item)
        # del self.rules
        # del self.file
        # del self.directory

    # def call_public_methods(self):
    #     attributes = (getattr(self.__class__, name) for name in dir(self.__class__) if not name.startswith('__'))
    #     class_methods = filter(inspect.ismethod, attributes)
    #     for rule in class_methods:
    #         rule()
    #
    #     # cleanup attributes afterwards so we can call vars() cleanly.
    #     del (self.rules)
    #     del (self.file)
    #     del (self.directory)

    def contains_expression(self):
        exp = self.directory.get('expression')
        if exp:
            pattern = re.compile(exp)
            search = pattern.finditer(self.file.file_name)
            for match in search:
                self.output_directories[self.directory.get('path')] = self.rules

    # def cleanup_attributes(self):
    #     del self.rules
    #     del self.file
    #     del self.directory









































# def return_all_methods():
#     attributes = (getattr(Rules, name) for name in dir(Rules))
#     methods = filter(inspect.ismethod, attributes)
#     return methods
#
#
# def compute_rule(file, directory, rule):
#     return rule(file, directory)
#
#
# def rule_has_expression(file, directory):
#     exp = directory.get('expression')
#
#     if exp:
#         pattern = re.compile(exp)
#         search = pattern.finditer(file.file_name)
#
#         for match in search:
#             return True
#
#     return False
#
#
# def rule_has_dates(file, directory):
#     created_before = directory.get('createdBefore')
#     created_after = directory.get('createdAfter')
#
#     # TODO: check date-time and validate.
#
#
# def rule_has_extension(file, directory):
#     has_extension = directory.get('hasExtension')
#
#     for extension in has_extension.split(','):
#         if file.extension.lower() in extension.lower():
#             return True
#     return False
#
#
# def rule_has_video(file, directory):
#     has_video = directory.get('hasVideo')
#
#     if has_video == 'True':
#         if file.v_stream:
#             return True
#
#     return False
#
#
# def rule_has_audio(file, directory):
#     has_audio = directory.get('hasAudio')
#
#     if has_audio == 'True':
#         if file.a_stream:
#             return True
#
#     return False
#
#
# def rule_has_image(file, directory):
#     has_image = directory.get('hasImage')
#
#     if has_image == 'True':
#         if file.i_stream:
#             return True
#
#     return False