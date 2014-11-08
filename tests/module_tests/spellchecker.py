# -*- coding:utf-8 -*-

import os

from hunspell import module_paths_from_filters, build_files

import common


class Manager(object):

    def __init__(self):

        self.builtSpellCheckers = {}

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):

        for path in self.builtSpellCheckers.iterkeys():
            os.remove(path + u".aff")
            os.remove(path + u".dic")

        try:
            os.rmdir(common.getBuildPath())
        except:
            pass

    def getUnusedCode(self):

        buildPath = common.getBuildPath()

        if not os.path.exists(buildPath):
            return 1

        index = 2
        while os.path.exists(os.path.join(buildPath, u"{}.aff".format(index))):
            index += 1
        return index

    def create(self, config):

        for builtPath, builtConfig in self.builtSpellCheckers.iteritems():
            if config == builtConfig:
                return builtPath

        module_paths = module_paths_from_filters(config,
                                                 language=config["language"])
        file_name = unicode(self.getUnusedCode())
        folder_path = common.getBuildPath()
        build_files(module_paths=module_paths, language=config["language"],
                    output_file_name=file_name, output_folder=folder_path)
        path = os.path.join(folder_path, file_name)
        self.builtSpellCheckers[path] = config
        return path
