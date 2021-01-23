import threading


class NewHandler:

    def __init__(self, xml_handler):
        self.active_threads = []
        self.xml_manager = xml_handler

    def spawn_new_thread(self, file, file_operation_schedule):
        t = threading.Thread(target=self.pipe(file, file_operation_schedule),)
        t.isDaemon()
        t.start()

    def pipe(self, file, file_operation_schedule):
        # Make a dict to hold a set of rules for a file.
        file_union = {}
        file_union['input_path'] = file.file_path
        file_union['output_paths'] = {}


        outputDirectories = self.xml_manager.return_dict()

        for directory in outputDirectories.get('outputDirectories'):

            # output_set = {}
            rules = {}

            if self.xml_manager.compute_rule(file, directory, self.xml_manager.rule_has_expression):
                file_union['output_paths'] = directory.get('path')
            if self.xml_manager.compute_rule(file, directory, self.xml_manager.contains_extensions):
                file_union['output_paths'] = directory.get('path')
            #TODO: CHECK DATETIME
            if self.xml_manager.compute_rule(file, directory, self.xml_manager.between_datetime):
                file_union['output_paths'] = directory.get('path')
            if self.xml_manager.compute_rule(file, directory, self.xml_manager.contains_video):
                file_union['output_paths'] = directory.get('path')
            if self.xml_manager.compute_rule(file, directory, self.xml_manager.contains_audio):
                file_union['output_paths'] = directory.get('path')
            if self.xml_manager.compute_rule(file, directory, self.xml_manager.contains_image):
                file_union['output_paths'] = directory.get('path')



        # # Check each file against each directory's set of rules.
        # for directory in output_directories.get['outputDirectories']:
        #     path = directory.get('path')



        # self.xml_manager.

        # Once rules are determined, add the dictionary to our operation schedule.
        file_operation_schedule[file.file_path] = rules