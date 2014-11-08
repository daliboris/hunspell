# -*- coding:utf-8 -*-

import codecs
from glob import glob
from imp import load_source
from importlib import import_module
import locale
from os import path, walk
import sys


def _root_dir():
    return path.join(path.dirname(__file__), "..")

root_path = _root_dir()
if root_path not in sys.path:
    sys.path.insert(0, path.join(root_path))

from hunspell import data_dir

import common

# See http://stackoverflow.com/a/4546129/939364
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)


def getFirstPathRelativeToSecondPathIfWithin(childPath, parentPath):
    absoluteChildPath = path.abspath(childPath)
    absoluteParentPath = path.abspath(parentPath)
    if (absoluteChildPath.startswith(absoluteParentPath)):
        childPath = absoluteChildPath[len(absoluteParentPath)+1:]
    return childPath


def load_generators():
    import generators
    generators_folder_path = path.join(path.dirname(__file__), "generators")
    root, languages, files = next(walk(generators_folder_path))
    generators_dictionary = {}
    for language in languages:
        import_module(u"generators."+language)
        generators_dictionary[language] = []
        language_generators_folder_path = path.join(
            generators_folder_path, language)
        if language_generators_folder_path not in sys.path:
            sys.path.insert(0, path.join(language_generators_folder_path))
        for generator_file_path in glob(
                language_generators_folder_path+"/*.py"):
            module_name = path.basename(generator_file_path)[:-3]
            module = load_source("generators.{}.{}".format(
                language, module_name), generator_file_path)
            if "loadGeneratorList" in module.__dict__:
                generators_dictionary[language].extend(module.loadGeneratorList())
    return generators_dictionary


# Program starts.
generators = load_generators()

for parameter in [parameter.decode('UTF-8') for parameter in sys.argv[1:]]:
    if parameter.startswith("-"):
        continue
    modulePath = getFirstPathRelativeToSecondPathIfWithin(parameter, data_dir())
    parts = modulePath.split(u"/")
    language = parts[0]
    if len(parts) > 1:
        modulePath = u"/".join(parts[1:])
    else:
        modulePath = u""
    usedGenerators = 0
    for generator in generators[language]:
        if generator.resource.startswith(modulePath):
            print u":: Actualizando «{resource}»…".format(resource=generator.resource)
            generator.run()
            usedGenerators += 1
    if usedGenerators == 0:
        print u":: Non existe ningún xerador para o módulo «{module}».".format(module=modulePath)