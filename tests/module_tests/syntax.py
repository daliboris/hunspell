# -*- coding:utf-8 -*-

from os import path, walk
import re
import subprocess

from hunspell import data_dir

import common
import test


unescapedSlash = re.compile(u"error: line (\d+): 0 is wrong flag id")
multipleDefinitions = re.compile(
    u"error: line (\d+): multiple definitions of an affix flag")


def check(path):

    errors = 0

    args = [
        u"hunspell",
        u"-d",
        path,
        u"-l",
    ]
    hunspell = subprocess.Popen(args, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    standardOutput, errorOutput = hunspell.communicate(u"proba")
    for line in errorOutput.splitlines():

        errors += 1

        match = unescapedSlash.match(line)
        if match:
            lineNumber = int(match.group(1))
            lineContent = common.getLineFromFile(path + u".dic", lineNumber)
            common.error(u"Hai unha barra inclinada («/») sen escapar na liña "
                         u"{} do dicionario («{}»).".format(
                             lineNumber, lineContent))
            continue

        match = multipleDefinitions.match(line)
        if match:
            lineNumber = int(match.group(1))
            lineContent = common.getLineFromFile(path + u".dic", lineNumber)
            common.error(u"Definición duplicada de marca na liña {} do "
                         u"dicionario («{}»).".format(lineNumber, lineContent))
            continue

        common.error(u"O executábel de Hunspell informou do seguinte erro: "
                     u"«{}».".format(line))

    return errors


class SyntaxTest(test.Test):

    def __init__(self, language):

        super(SyntaxTest, self).__init__()

        self.path = "{}/sintax".format(language)
        self.language = language

    def getAllModules(self, language):
        modules = []
        root, module_folders, module_files = next(walk(
            path.join(data_dir(), language).encode("utf-8")))
        for module in module_folders:
            modules.append(module.decode("utf-8"))
        for module in module_files:
            modules.append(module.decode("utf-8"))
        return modules

    def run(self, spellCheckerManager):
        modules = self.getAllModules(self.language)
        config = {
            "aff": modules,
            "dic": modules,
            "rep": modules,
            "language": self.language,
        }
        self.spellCheckerPath = spellCheckerManager.create(config)
        self.errors += check(self.spellCheckerPath)
        self.report()


def loadTestList():
    test_list = []
    root, languages, files = next(walk(data_dir()))
    for language in languages:
        if language != u"common":
            test_list.append(SyntaxTest(language))
    return test_list
