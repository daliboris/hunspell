# -*- coding:utf-8 -*-

from idiomatic.cache import ContentCache
from idiomatic.generators import Generator
from idiomatic.parsers import PdfParser

from formatting import formatEntriesAndCommentsForDictionary


uvigoContentCache = ContentCache("hunspell/gl/uvigo")
doubtsPdfUrl = u"http://anl.uvigo.es/UserFiles/File/manuais/" \
    u"Lingua_galega._Dubidas_linguisticas.pdf"


class AbbreviationsGenerator(Generator):

    def __init__(self):
        super(AbbreviationsGenerator, self).__init__()
        self.resource = u"uvigo/abreviaturas.dic"

    def parseSubEntries(self, entry):
        if u"," in entry:
            for subentry in entry.split(u","):
                yield subentry
        elif u"/ /" in entry:
            for subentry in entry.split(u"/ /"):
                yield subentry
        elif u"/" in entry:
            for subentry in entry.split(u"/"):
                yield subentry
        else:
            yield entry

    def content(self):

        filePath = uvigoContentCache.downloadFileIfNeededAndGetLocalPath(
            doubtsPdfUrl)
        pdfParser = PdfParser(filePath)

        entries = {}
        parsingStage = 0

        for line in pdfParser.lines():

            if parsingStage == 0:
                if line == u"Relación de abreviaturas máis frecuentes":
                    parsingStage += 1
                else:
                    continue

            elif parsingStage == 1:
                if line == u"Relación de siglas e acrónimos máis frecuentes":
                    parsingStage += 1
                    continue

            elif parsingStage == 2:
                if line == u"49":
                    parsingStage += 1
                else:
                    continue

            elif parsingStage == 3:
                if line == u"5":
                    break

            if u":" in line:
                comment, entry = line.split(u":")
                for subentry in self.parseSubEntries(entry):
                    subentry = subentry.strip()
                    entries[subentry] = comment.strip()

        dictionary = u"# Relación de abreviaturas máis frecuentes\n"
        dictionary += u"# {}\n".format(doubtsPdfUrl)
        dictionary += u"\n"
        for entry in formatEntriesAndCommentsForDictionary(entries,
                                                           u"abreviatura"):
            dictionary += entry
        return dictionary


class AcronymsGenerator(Generator):

    def __init__(self):
        super(AcronymsGenerator, self).__init__()
        self.resource = u"uvigo/siglas.dic"

    def content(self):

        filePath = uvigoContentCache.downloadFileIfNeededAndGetLocalPath(
            doubtsPdfUrl)
        pdfParser = PdfParser(filePath)

        entries = {}
        parsingStage = 0
        commentCache = None

        for line in pdfParser.lines():

            if parsingStage == 0:
                if line == u"Relación de siglas e acrónimos máis frecuentes":
                    parsingStage += 1
                else:
                    continue

            elif parsingStage == 1:
                if line == u"49":
                    parsingStage += 1
                    continue

            elif parsingStage == 2:
                if line == u"5":
                    parsingStage += 1
                else:
                    continue

            elif parsingStage == 3:
                if line == u"55":
                    break

            if commentCache:
                entry = line.strip()
                entries[entry] = commentCache
                commentCache = None
            elif u":" in line:
                comment, entry = line.split(u":")
                entry = entry.strip()
                if entry:
                    entries[entry] = comment.strip()
                else:
                    commentCache = comment.strip()

        dictionary = u"# Relación de acrónimos e siglas máis frecuentes\n"
        dictionary += u"# {}\n".format(doubtsPdfUrl)
        dictionary += u"\n"
        for entry in formatEntriesAndCommentsForDictionary(entries, u"sigla"):
            dictionary += entry
        return dictionary


def generators():
    generators = []
    generators.append(AbbreviationsGenerator())
    generators.append(AcronymsGenerator())
    return generators
