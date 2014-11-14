# -*- coding:utf-8 -*-

from idiomatic.cache import ContentCache
from idiomatic.generators import Generator
from idiomatic.parsers import PdfParser

from formatting import formatEntriesAndCommentsForDictionary


contentCache = ContentCache("hunspell/gl/usc")
pdfUrl = u"http://www.usc.es/export/sites/default/gl/servizos/snl/" \
    u"asesoramento/fundamentos/descargas/abreviaturassiglassimboloslexico.pdf"


class AbbreviationsGenerator(Generator):

    def __init__(self):
        super(AbbreviationsGenerator, self).__init__()
        self.resource = u"usc/abreviaturas.dic"

    def parseEntry(self, entry):
        if u"./" in entry:
            for subentry in entry.split(u"/"):
                subentry = subentry.strip()
                if subentry:
                    yield subentry
        elif u"," in entry:
            for subentry in entry.split(u","):
                subentry = subentry.strip()
                if subentry:
                    yield subentry
        elif entry:
            yield entry

    def content(self):

        filePath = contentCache.downloadFileIfNeededAndGetLocalPath(pdfUrl)
        pdfParser = PdfParser(filePath)

        entries = {}
        parsingStage = 0
        lineIsContinuation = False
        comment = None

        for line in pdfParser.lines():

            if comment and line[0] != u" " and parsingStage == 1:
                lineIsContinuation = True
            line = line.strip()

            if parsingStage == 0:
                if line == u"abril":
                    parsingStage += 1
                else:
                    continue

            elif parsingStage == 1:
                if line == u"Manuel Bermúdez":
                    break

            if line.startswith(u"Abreviaturas, siglas, símbolos e léxico"):
                continue
            if line.isdigit():
                continue

            if lineIsContinuation:
                lineIsContinuation = False
                comment += u" " + line
                continue

            if comment:
                for subentry in self.parseEntry(line):
                    entries[subentry] = comment
                comment = None
            else:
                comment = line

        dictionary = u"# Relación de abreviaturas máis frecuentes\n"
        dictionary += u"# {}\n".format(pdfUrl)
        dictionary += u"\n"
        for entry in formatEntriesAndCommentsForDictionary(entries,
                                                           u"abreviatura"):
            dictionary += entry
        return dictionary


class AcronymsGenerator(Generator):

    def __init__(self):
        super(AcronymsGenerator, self).__init__()
        self.resource = u"usc/siglas.dic"

    def content(self):

        filePath = contentCache.downloadFileIfNeededAndGetLocalPath(pdfUrl)
        pdfParser = PdfParser(filePath)

        entries = {}
        parsingStage = 0
        lineIsContinuation = False
        comment = None

        for line in pdfParser.lines():

            if comment and line[0] != u" " and parsingStage == 1:
                lineIsContinuation = True
            line = line.strip()

            if parsingStage == 0:
                if line == u"Asociación Española de Normalización e " \
                        u"Certificación":
                    parsingStage += 1
                else:
                    continue

            elif parsingStage == 1:
                if line == u"A sigla caracterízase por:":
                    break

            if line.isdigit():
                continue

            if lineIsContinuation:
                lineIsContinuation = False
                comment += u" " + line
                continue

            if comment:
                entries[line] = comment
                comment = None
            else:
                comment = line

        dictionary = u"# Relación de siglas e acrónimos máis frecuentes\n"
        dictionary += u"# {}\n".format(pdfUrl)
        dictionary += u"\n"
        for entry in formatEntriesAndCommentsForDictionary(entries, u"sigla"):
            dictionary += entry
        return dictionary


class SymbolsGenerator(Generator):

    def __init__(self):
        super(SymbolsGenerator, self).__init__()
        self.resource = u"usc/símbolos.dic"

    def parseEntry(self, entry):
        if u"./" in entry:
            for subentry in entry.split(u"/"):
                subentry = subentry.strip()
                if subentry:
                    yield subentry
        elif u"," in entry:
            for subentry in entry.split(u","):
                subentry = subentry.strip()
                if subentry:
                    yield subentry
        elif entry:
            yield entry

    def content(self):

        filePath = contentCache.downloadFileIfNeededAndGetLocalPath(pdfUrl)
        pdfParser = PdfParser(filePath)

        entries = {}
        parsingStage = 0
        lineIsContinuation = False
        comment = None

        for line in pdfParser.lines():

            if comment and line[0] != u" " and parsingStage == 1:
                lineIsContinuation = True
            line = line.strip()

            if parsingStage == 0:
                if line == u"amperio":
                    parsingStage += 1
                else:
                    continue

            elif parsingStage == 1:
                if line == u"Manuel Bermúdez":
                    break

            if line.isdigit():
                continue

            if lineIsContinuation:
                lineIsContinuation = False
                comment += u" " + line
                continue

            if comment:
                if not comment.endswith("-"):  # Saltarse os prefixos.
                    for subentry in self.parseEntry(line):
                        entries[subentry] = comment
                comment = None
            else:
                comment = line

        dictionary = u"# Relación de símbolos máis frecuentes\n"
        dictionary += u"# {}\n".format(pdfUrl)
        dictionary += u"\n"
        for entry in formatEntriesAndCommentsForDictionary(entries,
                                                           u"símbolo"):
            dictionary += entry
        return dictionary


def generators():
    generators = []
    generators.append(AbbreviationsGenerator())
    generators.append(AcronymsGenerator())
    generators.append(SymbolsGenerator())
    return generators
