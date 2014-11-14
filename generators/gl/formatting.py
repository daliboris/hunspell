# -*- coding:utf-8 -*-

import re

from idiomatic.languages import collator
from idiomatic.ui import ProgressReporter

from words import wordsToIgnore


numberPattern = re.compile(u"^[0-9-]*[0-9]+(\.?[ºª]|[.°:])?$")


def formatEntriesForDictionary(entries, partOfSpeech):
    return formatEntriesAndCommentsForDictionary(dict.fromkeys(entries, None),
                                                 partOfSpeech)


def escapeSpecialEntryCharacters(entry):
    return entry.replace("/", "\/")


def formatEntriesAndCommentsForDictionary(entries, partOfSpeech):
    reporter = ProgressReporter(
        u"Adaptando as entradas ao formato do dicionario", len(entries))
    for entry in sorted(entries, cmp=collator("gl").compare):
        if " " in entry:  # Use special syntax in .dic if there are spaces.
            ngramas = set()
            for ngrama in entry.split(u" "):
                ngrama = ngrama.strip(",")
                if ngrama == u"/":  # e.g. «Alianza 90 / Os Verdes».
                    continue
                # Ignore general vocabulary.
                if ngrama not in wordsToIgnore:
                    # Do not repeat ngrams within the same entry.
                    if ngrama not in ngramas:
                        # Hunspell always allows numbers.
                        if not numberPattern.match(ngrama):
                            ngramas.add(ngrama)
                            if entries[entry]:  # Entry has a comment.
                                yield u"{ngrama} po:{partOfSpeech} " \
                                      u"[n-grama: {entry}]  " \
                                      u"# {comment}\n".format(
                                          ngrama=escapeSpecialEntryCharacters(
                                              ngrama),
                                          entry=entry,
                                          partOfSpeech=partOfSpeech,
                                          comment=entries[entry])
                            else:
                                yield u"{ngrama} po:{partOfSpeech} " \
                                      u"[n-grama: {entry}]\n".format(
                                          ngrama=escapeSpecialEntryCharacters(
                                              ngrama),
                                          entry=entry,
                                          partOfSpeech=partOfSpeech)
        else:
            if entry not in wordsToIgnore and not numberPattern.match(entry):
                if entries[entry]:  # Entry has a comment.
                    yield u"{entry} po:{partOfSpeech}  # {comment}\n".format(
                        entry=escapeSpecialEntryCharacters(entry),
                        partOfSpeech=partOfSpeech, comment=entries[entry])
                else:
                    yield u"{entry} po:{partOfSpeech}\n".format(
                        entry=escapeSpecialEntryCharacters(entry),
                        partOfSpeech=partOfSpeech)
        reporter.increase()
    reporter.done()
