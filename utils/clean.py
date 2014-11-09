# -*- coding:utf-8 -*-

import codecs
import locale
from os import path, walk
import sys

# See http://stackoverflow.com/a/4546129/939364
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)


# Program starts.

fileToClean = sys.argv[1]
inputFilesOrFolders = sys.argv[2:]

entries = set()
for inputFileOrFolder in inputFilesOrFolders:
    if path.isfile(inputFileOrFolder):
        with codecs.open(inputFileOrFolder, "r", "utf-8") as fileObject:
            for line in fileObject.readlines():
                entries.add(line.split(u" ")[0])
    else:
        for parentFolderPath, folderNames, fileNames in \
                walk(inputFileOrFolder.decode("utf-8")):
            for fileName in fileNames:
                if fileName.endswith(u".dic"):
                    filePath = path.join(parentFolderPath, fileName)
                    if filePath != fileToClean:
                        with codecs.open(filePath, "r", "utf-8") as fileObject:
                            for line in fileObject.readlines():
                                entries.add(line.split(u" ")[0])


newContent = u""
with codecs.open(fileToClean, "r", "utf-8") as fileObject:
    for line in fileObject.readlines():

        strippedLine = line.strip()
        if not strippedLine or strippedLine[0] == u"#":
            newContent += line
            continue

        entry = line.split(u" ")[0].strip()
        if entry not in entries:
            newContent += line
            continue

        print u"Eliminando «{}»…".format(entry)


with codecs.open(fileToClean, "w", "utf-8") as fileObject:
    fileObject.write(newContent)
