#!/usr/bin/env python2
# -*- coding:utf-8 -*-

"""API to work with data from the **Hunspell** repository."""

import codecs
import json
from os import makedirs, path, sep
import re
import sys


def _root_dir():
    return path.abspath(path.dirname(__file__))


def _external_dir():
    return path.join(_root_dir(), "external")


sys.path.append(path.join(_external_dir(), "pydiomatic"))
from idiomatic.data import filters_to_paths
from idiomatic.languages import collator

sys.path.append(path.join(_external_dir(), "lexicon"))
from lexicon import load_word_data


def data_dir():
    """Returns an absolute path to the data folder of this repository."""
    return path.join(_root_dir(), "data")


def _lexicon_data_dir():
    return path.join(_external_dir(), "lexicon", "data")


def data_dirs():
    """Returns a list with the absolute paths to the data folders of this
    repository and external repositories that are dependencies of this
    repository."""
    return [_lexicon_data_dir(), data_dir()]


def _strip_comments(line):
    index = line.find('#')
    if index < 0:
        return line
    return line[0:index]


def _simplify_spacing(line):
    line = line.replace('\t', ' ')
    line = re.sub(' +', ' ', line)
    return line


def _strip_line(line):
    line = _strip_comments(line)
    line = line.rstrip() + '\n'
    line = _simplify_spacing(line)
    return line


def _line_is_useless(line):
    strippedLine = line.strip()
    if strippedLine == "" or strippedLine[0] == "#":
        return True
    return False


def _load_and_strip(file_path):
    parsed_content = u""
    with codecs.open(file_path, "r", "utf-8") as fp:
        for line in fp:
            if not _line_is_useless(line):
                parsed_content += _strip_line(line)
    return parsed_content


def _load_files_and_strip(file_paths):
    content = u""
    for file_path in file_paths:
        content += _load_and_strip(file_path)
    return content


def _lines_to_rep(lines, language):
    content = u""
    if lines:
        content = u"REP {}\n".format(len(lines))
        for line in sorted(lines, cmp=collator(language).compare):
            content += u"REP {}\n".format(line)
    return content


def _remove_duplicate_lines(lines):
    unique_lines = set()
    for line in lines:
        unique_lines.add(line)
    return unique_lines


def _load_rep_lines(module_paths):
    unparsed_content = _load_files_and_strip(module_paths)
    return _remove_duplicate_lines(unparsed_content.splitlines())


def _language_and_module_from_path(module_path):
    parts = module_path.split(sep)
    data_index = len(parts)-1
    while parts[data_index] != "data":
        data_index -= 1
    return parts[data_index+1], sep.join(parts[data_index+2:])


def _map_word_inflections(source_inflections, target_inflections):
    mapping = []
    if len(source_inflections) == 1:
        for target_inflection in target_inflections:
            mapping.append([source_inflections[0][0], target_inflection[0]])
    elif len(target_inflections) == 1:
        for source_inflection in source_inflections:
            mapping.append([source_inflection[0], target_inflections[0][0]])
    else:
        for source_inflection in source_inflections:
            for target_inflection in target_inflections:
                if source_inflection[1] == target_inflection[1]:
                    mapping.append([source_inflection[0],
                                    target_inflection[0]])
    return mapping


def _load_rep_json_lines(module_paths):
    lines = set()
    for module_path in module_paths:
        with open(module_path, "rb") as fp:
            data = json.load(fp)
        language, module = _language_and_module_from_path(module_path)
        for source, target in data:
            source_data = load_word_data(source, language=language,
                                         search_from=module)
            target_data = load_word_data(target, language=language,
                                         search_from=module)
            mapping = _map_word_inflections(source_data["inflections"],
                                            target_data["inflections"])
            for source_word, target_word in mapping:
                lines.add(u"^{}$ {}".format(source_word, target_word))
    return lines


def _load_suggestion_rules(module_paths, language):
    lines = set()
    if "rep" in module_paths:
        lines |= _load_rep_lines(module_paths["rep"])
    if "rep.json" in module_paths:
        lines |= _load_rep_json_lines(module_paths["rep.json"])
    return _lines_to_rep(lines, language=language)


def _build_aff(module_paths, output_file_path, language):
    content = _load_and_strip(path.join(data_dir(), language, u"base.aff"))
    content += _load_files_and_strip(module_paths["aff"])
    content += _load_suggestion_rules(module_paths, language=language)
    with codecs.open(output_file_path, "w", "utf-8") as fp:
        fp.write(content)


def _lines_to_dic(lines, language):
    content = u""
    if lines:
        content += u"{}\n".format(len(lines))
        for line in sorted(lines, cmp=collator(language).compare):
            content += u"{}\n".format(line)
    return content


def _load_dic(module_paths, language):
    unparsed_content = _load_files_and_strip(module_paths)
    unique_lines = _remove_duplicate_lines(unparsed_content.splitlines())
    return _lines_to_dic(unique_lines, language=language)


def _build_dic(module_paths, output_file_path, language):
    content = _load_dic(module_paths["dic"], language=language)
    with codecs.open(output_file_path, "w", "utf-8") as fp:
        fp.write(content)


def build_files(module_paths, language, output_file_name, output_folder):
    """Builds the specified *module_paths* of the specified *language* into
    Hunspell files. The resulting files are generated on the specified
    *output_folder* with the specified *output_file_name*.

    The *module_paths* parameter must be a dictionary. The dictionary may
    contain some of the keys in the list below. Those keys represent file
    extensions that the **Hunspell** repository understands, and their value
    must be a list of module files with that file extension.

    * :code:`aff`, for rule modules.
    * :code:`dic`, for lemma modules.
    * :code:`rep`, for suggestion modules of the **Hunspell** repository.
    * :code:`rep.json`, for suggestion modules of the **Spelling** repository.

    You can obtain a dictionary of module paths from a dictionary of module
    filters using :py:func:`module_paths_from_filters`.

    Any other keys in the *module_paths* dictionary are ignored.
    """
    if not path.exists(output_folder):
        makedirs(output_folder)
    _build_aff(module_paths,
               path.join(output_folder, output_file_name + ".aff"),
               language=language)
    _build_dic(module_paths,
               path.join(output_folder, output_file_name + ".dic"),
               language=language)


def _extension_to_content_type(extension):
    if extension == "rep.json":
        return "rep"
    else:
        return extension


def module_paths_from_filters(filters, language):
    """Given a dictionary of *filters*, where keys are types of filters for the
    **Hunspell** repository (:code:`aff`, :code:`dic` or :code:`rep`) and their
    values are `module filters`_, it returns a new dictionary that contains
    file extensions as keys and lists of paths to module files with those
    file extensions as values.

    The return value can be passed to :py:func:`build_files`.

    .. _module filters: http://pydiomatic.rtfd.org/en/latest/data.html#modules
    """
    module_paths = {}
    for extension in ["aff", "dic", "rep", "rep.json"]:
        type = _extension_to_content_type(extension)
        if type in filters:
            module_paths[extension] = filters_to_paths(
                filters[type], language=language, extension=extension,
                search_paths=data_dirs())
    return module_paths


def _unmunch_files(aff_path, dic_path, output_file_path):
    from subprocess import Popen, PIPE
    unmunch_script = path.join(_root_dir(), "utils", "unmunch.sh")
    command = u"bash \"{}\" \"{}\" \"{}\" >> \"{}\"".format(
        unmunch_script, dic_path, aff_path, output_file_path)
    process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    process.communicate()


def unmunch(language, aff_filters, dic_filters, rep_filters, output_file_path):
    """Generates a list of words accepted by a spellchecker built from the
    specified modules (*aff_filters*, *dic_filters*, *rep_filters*) for the
    specified *language*, and stores those words on the specified
    *output_file_path*, one word per line."""
    from tempfile import mkdtemp
    temporary_folder = mkdtemp(prefix=u"hunspell")
    base_name = language
    aff_path = path.join(temporary_folder, base_name + u".aff")
    dic_path = path.join(temporary_folder, base_name + u".dic")
    build_files(aff_filters=aff_filters, dic_filters=dic_filters,
                rep_filters=rep_filters, language=language,
                output_file_path=base_name, output_folder=temporary_folder)
    _unmunch_files(aff_path=aff_path, dic_path=dic_path,
                   output_file_path=output_file_path)
    from shutil import rmtree
    rmtree(temporary_folder)
