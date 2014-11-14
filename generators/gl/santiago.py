# -*- coding:utf-8 -*-

from idiomatic.cache import ContentCache
from idiomatic.generators import Generator
from idiomatic.parsers import PdfParser

from formatting import formatEntriesAndCommentsForDictionary


contentCache = ContentCache("hunspell/gl/santiago")
styleGuidePdfUrl = u"http://www.v1deputacionlugo.org/media/documentos/" \
    u"Libro_de_estilo_Concello_Santiago.pdf"


class AbbreviationsGenerator(Generator):

    def __init__(self):
        super(AbbreviationsGenerator, self).__init__()
        self.resource = u"santiago/abreviaturas.dic"

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

        filePath = contentCache.downloadFileIfNeededAndGetLocalPath(
            styleGuidePdfUrl)
        pdfParser = PdfParser(filePath)

        entries = {}
        parsingStage = 0
        continuesInTheNextLine = False
        previousLine = None

        import re
        import string

        plural = re.compile(u"\(plural ([^)]+)\)")
        fem = re.compile(u"\(fem. ([^)]+)\)")
        parenthesis = re.compile(u" *\([^)]*\)")

        for line in pdfParser.lines():

            if line[-1:] == u" " and parsingStage == 1:
                continuesInTheNextLine = True
            line = line.strip()

            if parsingStage == 0:
                if line == u"7.1.2 Listaxe de abreviaturas":
                    parsingStage += 1
                continue

            elif parsingStage == 1:
                if line == u"7.2 A sigla":
                    break

            if line in string.uppercase:
                continue
            if line.startswith(u"Ortografía e estilo"):
                continue
            if line.isdigit():
                continue

            if continuesInTheNextLine:
                continuesInTheNextLine = False
                previousLine = line
                continue

            if previousLine:
                line = previousLine + u" " + line
                previousLine = None

            try:
                comment, entry = line.split(u":")
            except ValueError:
                parts = line.split(u":")
                comment = u":".join(parts[:-1])
                entry = parts[-1]

            subentries = set()

            for match in plural.finditer(entry):
                for subentry in self.parseEntry(match.group(1)):
                    subentries.add(subentry)

            for match in fem.finditer(entry):
                for subentry in self.parseEntry(match.group(1)):
                    subentries.add(subentry)

            # Eliminar contido entre parénteses.
            entry = re.sub(parenthesis, u"", entry)
            entry = entry.strip()

            for subentry in self.parseEntry(entry):
                subentries.add(subentry)

            for subentry in subentries:
                entries[subentry] = comment

        dictionary = u"# Relación de abreviaturas máis frecuentes na " \
            u"linguaxe administrativa\n"
        dictionary += u"# {}\n".format(styleGuidePdfUrl)
        dictionary += u"\n"
        for entry in formatEntriesAndCommentsForDictionary(entries,
                                                           u"abreviatura"):
            dictionary += entry
        return dictionary


class AcronymsGenerator(Generator):

    def __init__(self):
        super(AcronymsGenerator, self).__init__()
        self.resource = u"santiago/siglas.dic"

    def content(self):

        filePath = contentCache.downloadFileIfNeededAndGetLocalPath(
            styleGuidePdfUrl)
        pdfParser = PdfParser(filePath)

        entries = {}
        parsingStage = 0
        continuesInTheNextLine = False
        previousLine = None

        import string

        for line in pdfParser.lines():

            if line[-1:] in [u" ", u"-"] and parsingStage == 1:
                continuesInTheNextLine = True

            if parsingStage == 0:
                if line == u"7.2.2 Listaxe de siglas e acrónimos de uso común":
                    parsingStage += 1
                continue

            elif parsingStage == 1:
                if line == u"7.3 O símbolo":
                    break

            if line in string.uppercase:
                continue
            if line.startswith(u"Ortografía e estilo"):
                continue
            if line.isdigit():
                continue

            if previousLine:
                line = previousLine + line
                previousLine = None

            if continuesInTheNextLine:
                continuesInTheNextLine = False
                previousLine = line
                continue

            if u":" not in line:
                parts = line.split(u" ")
                entry = parts[0]
                comment = u" ".join(parts[1:])
            else:
                try:
                    entry, comment = line.split(u":")
                except ValueError:
                    parts = line.split(u":")
                    entry = parts[0]
                    comment = u":".join(parts[1:])

            entries[entry.strip()] = comment

        dictionary = u"# Relación de siglas máis frecuentes\n"
        dictionary += u"# {}\n".format(styleGuidePdfUrl)
        dictionary += u"\n"
        for entry in formatEntriesAndCommentsForDictionary(entries, u"sigla"):
            dictionary += entry
        return dictionary


class SymbolsGenerator(Generator):

    def __init__(self):
        super(SymbolsGenerator, self).__init__()
        self.resource = u"santiago/símbolos.dic"

    def parseEntry(self, entry):
        # http://stackoverflow.com/a/13875688/939364
        entry = u''.join(
            dict(zip(u"0123456789", u"⁰¹²³⁴⁵⁶⁷⁸⁹")).get(c, c) for c in entry)
        if u" ou " in entry:
            for subentry in entry.split(u" ou "):
                subentry = subentry.strip()
                if subentry:
                    yield subentry
        elif entry in [u"MXP/MXN", u"PES/PEN", u"ROL/RON", u"TRL/TRY"]:
            for subentry in entry.split(u"/"):
                subentry = subentry.strip()
                if subentry:
                    yield subentry
        elif entry.endswith(u"-") or entry.startswith(u"-"):
            pass  # Prefixo ou sufixo.
        elif entry:
            yield entry

    def content(self):

        filePath = contentCache.downloadFileIfNeededAndGetLocalPath(
            styleGuidePdfUrl)
        pdfParser = PdfParser(filePath)

        entries = {}
        parsingStage = 0
        continuesInTheNextLine = False
        previousLine = None

        for line in pdfParser.lines():

            if line[-1:] in [u" ", u"-"] and parsingStage == 1:
                continuesInTheNextLine = True

            if parsingStage == 0:
                if line == u"7.3.2 Listaxe de símbolos de uso común":
                    parsingStage += 1
                continue

            elif parsingStage == 1:
                if line == u"7.4 O acrónimo":
                    break

            if line.startswith(u"Ortografía e estilo"):
                continue
            if line.isdigit():
                continue

            if previousLine:
                line = previousLine + line
                previousLine = None

            if continuesInTheNextLine:
                continuesInTheNextLine = False
                previousLine = line
                continue

            if u":" not in line:
                parts = line.split(u" ")
                entry = parts[0]
                comment = u" ".join(parts[1:])
            else:
                try:
                    entry, comment = line.split(u":")
                except ValueError:
                    parts = line.split(u":")
                    entry = parts[0]
                    comment = u":".join(parts[1:])

            entry = entry.strip()
            for subentry in self.parseEntry(entry):
                entries[subentry] = comment

        dictionary = u"# Relación de símbolos máis frecuentes\n"
        dictionary += u"# {}\n".format(styleGuidePdfUrl)
        dictionary += u"\n"
        for entry in formatEntriesAndCommentsForDictionary(entries,
                                                           u"símbolo"):
            dictionary += entry
        return dictionary


def generators():
    generators = []
    generators.append(AcronymsGenerator())
    generators.append(AbbreviationsGenerator())
    generators.append(SymbolsGenerator())
    return generators
