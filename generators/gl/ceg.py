# -*- coding:utf-8 -*-

from idiomatic.cache import ContentCache
from idiomatic.generators import Generator
from idiomatic.parsers import PdfParser

from formatting import formatEntriesAndCommentsForDictionary


contentCache = ContentCache("hunspell/gl/ceg")
pdfUrl = u"http://www.normalizacion.ceg.es/attachments/article/71/" \
    u"siglaspdf.pdf"


class AbbreviationsGenerator(Generator):

    def __init__(self):
        super(AbbreviationsGenerator, self).__init__()
        self.resource = u"ceg/abreviaturas.dic"

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
        elif u";" in entry:
            for subentry in entry.split(u";"):
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
        entry = None

        import re

        plural = re.compile(u"\(pl. ([^)]+)\)")
        parenthesis = re.compile(u" *\([^)]*\)")

        for line in pdfParser.lines():

            line = line.strip()
            if not line:
                continue
            if line.isdigit():
                continue

            if parsingStage == 0:
                if line == u"ABREVIATURAS:":
                    parsingStage += 1
                continue

            elif parsingStage == 1:
                if line == u"SÍMBOLOS:":
                    break

            parts = line.split(u":")
            comment = parts[0].strip()
            entry = u":".join(parts[1:]).strip()

            subentries = set()

            for match in plural.finditer(entry):
                for subentry in self.parseEntry(match.group(1)):
                    subentries.add(subentry)

            # Eliminar contido entre parénteses.
            entry = re.sub(parenthesis, u"", entry)
            entry = entry.strip()

            for subentry in self.parseEntry(entry):
                if subentry.endswith(u"o/a."):
                    subentries.add(subentry[:-4] + u"a.")
                    subentries.add(subentry[:-4] + u"o.")
                else:
                    subentries.add(subentry)

            for subentry in subentries:
                entries[subentry] = comment

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
        self.resource = u"ceg/siglas.dic"

    def content(self):

        filePath = contentCache.downloadFileIfNeededAndGetLocalPath(pdfUrl)
        pdfParser = PdfParser(filePath)

        entries = {}
        parsingStage = 0
        entry = None

        comment = u""
        for line in pdfParser.lines():

            line = line.strip()
            if not line:
                continue

            if parsingStage == 0:
                if line == u"SIGLAS e ACRÓNIMOS":
                    parsingStage += 1
                continue

            elif parsingStage == 1:
                if line == u"ABREVIATURAS:":
                    break

            if line.isdigit():
                continue

            parts = line.split(u":")
            if parts[0].upper() != parts[0]:
                comment += u" " + parts[0].strip()
                entries[entry] = comment
            else:
                entry = parts[0].strip()
                comment = u":".join(parts[1:]).strip()
                entries[entry] = comment

        dictionary = u"# Relación de siglas e acrónimos máis frecuentes\n"
        dictionary += u"# {}\n".format(pdfUrl)
        dictionary += u"\n"
        for entry in formatEntriesAndCommentsForDictionary(entries, u"sigla"):
            dictionary += entry
        return dictionary


class SymbolsGenerator(Generator):

    def __init__(self):
        super(SymbolsGenerator, self).__init__()
        self.resource = u"ceg/símbolos.dic"

    def content(self):

        filePath = contentCache.downloadFileIfNeededAndGetLocalPath(pdfUrl)
        pdfParser = PdfParser(filePath)

        entries = {}
        parsingStage = 0

        for line in pdfParser.lines():

            line = line.strip()
            if not line:
                continue

            if parsingStage == 0:
                if line == u"SÍMBOLOS:":
                    parsingStage += 1
                continue

            elif parsingStage == 1:
                if line == u"CASOS ESPECIAIS:":
                    break

            if line.isdigit():
                continue

            parts = line.split(u":")
            comment = parts[0].strip()
            entry = u":".join(parts[1:]).strip()
            if comment in [u"FM"]:  # Entradas invertidas.
                temporary = comment
                comment = entry
                entry = temporary
            if u"," in entry:
                for subentry in entry.split(u","):
                    entries[subentry.strip()] = comment
            else:
                entries[entry] = comment

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
