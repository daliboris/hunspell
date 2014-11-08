# -*- coding:utf-8 -*-

import codecs
import locale
from os import path
import sys


def root_dir():
    return path.join(path.dirname(__file__), "..", "..")

root_path = root_dir()
if root_path not in sys.path:
    sys.path.insert(0, path.join(root_path))

import common
import spellchecker
import spelling
import syntax

# See http://stackoverflow.com/a/4546129/939364
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)


def loadBuiltInTestList():
    builtInTests = []
    builtInTests.extend(spelling.loadTestList())
    builtInTests.extend(syntax.loadTestList())
    return builtInTests


def run_test(test, manager):
    print(u":: Running test ‘{path}’…".format(path=test.path))
    test.run(manager)


testsPath = common.getTestsPath()
builtInTests = loadBuiltInTestList()

with spellchecker.Manager() as spellCheckerManager:
    parameters = sys.argv[1:]
    if parameters:
        for parameter in [parameter.decode("utf-8")
                          for parameter in parameters]:
            testPath = common.getFirstPathRelativeToSecondPathIfWithin(
                parameter, testsPath)
            executedTests = 0
            for test in builtInTests:
                if test.path.startswith(testPath):
                    run_test(test, spellCheckerManager)
                    executedTests += 1
            if executedTests == 0:
                print u":: There is no test for path ‘{path}’.".format(
                    path=testPath)
    else:
        for test in builtInTests:
            run_test(test, spellCheckerManager)
