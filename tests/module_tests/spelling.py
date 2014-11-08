# -*- coding:utf-8 -*-

import codecs
import os
import subprocess

import common
import syntax
import test


class SpellingTest(test.Test):

    def __init__(self, path):

        super(SpellingTest, self).__init__()

        self.path = path
        self._config = None
        self._language = path.split(u"/")[0]

        self.spellCheckerPath = None
        self.spellCheckerManager = None

    def config(self):
        if self._config is None:
            import json
            with codecs.open(
                    os.path.join(common.module_tests_data_path(),
                                 self.path + u".json"),
                    "r", "utf-8") as fileObject:
                self._config = json.load(fileObject)
            self._config["language"] = self._language
            for option in []:
                if option not in self._config:
                    self._config[option] = []
        return self._config

    def generateSpellChecker(self):
        config = self.config()
        self.spellCheckerPath = self.spellCheckerManager.create(config)
        self.errors += syntax.check(self.spellCheckerPath)

    def iterFileLines(self, path):
        if os.path.exists(path):
            with codecs.open(path, "r", "utf-8") as fileObject:
                for line in fileObject:
                    if u"#" in line:
                        line = line.split(u"#")[0]
                    line = line.strip()
                    if line:
                        yield line

    def passes(self, line):
        args = [
            u"hunspell",
            u"-d",
            self.spellCheckerPath,
            u"-l",
        ]
        hunspell = subprocess.Popen(args, stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        standardOutput, errorOutput = hunspell.communicate(
            line.encode("utf-8"))
        return not standardOutput.decode("utf-8").strip()

    def analyze(self, line):
        args = [
            u"hunspell",
            u"-d",
            self.spellCheckerPath,
            u"-m",
        ]
        hunspell = subprocess.Popen(args, stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        standardOutput, errorOutput = hunspell.communicate(
            u"\"{}\"".format(line).encode("utf-8"))
        return standardOutput.decode("utf-8")

    def checkGoodInput(self):
        goodInputFilePath = os.path.join(
            common.getTestsPath(), u"{}.good".format(self.path))
        for line in self.iterFileLines(goodInputFilePath):
            if not self.passes(line):
                common.error(u"O corrector non aceptou «{}».".format(line))
                details = self.analyze(line)
                common.details(details)
                self.errors += 1

    def checkBadInput(self):
        badInputFilePath = os.path.join(common.getTestsPath(),
                                        u"{}.bad".format(self.path))
        for line in self.iterFileLines(badInputFilePath):
            if self.passes(line):
                common.error(u"O corrector aceptou «{}».".format(line))
                common.details(self.analyze(line))
                self.errors += 1

    def run(self, spellCheckerManager):
        self.spellCheckerManager = spellCheckerManager
        self.generateSpellChecker()
        self.checkGoodInput()
        self.checkBadInput()
        self.report()


def findJsonFilePaths(rootPath):
    for parentFolderPath, folderNames, fileNames in os.walk(
            rootPath.encode("utf-8")):
        for fileName in fileNames:
            fileName = fileName
            if fileName.endswith(u".json"):
                yield os.path.join(parentFolderPath, fileName).decode("utf-8")


def loadTestList():
    tests = []
    module_tests_data_path = common.module_tests_data_path()
    for jsonFilePath in findJsonFilePaths(module_tests_data_path):
        testPath = common.getFirstPathRelativeToSecondPathIfWithin(
            jsonFilePath[:-5], module_tests_data_path)
        tests.append(SpellingTest(testPath))
    return tests
