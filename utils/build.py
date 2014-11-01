#!/usr/bin/env python2
# -*- coding:utf-8 -*-

"""Build a set of Hunspell spellchecking files.

Run this script to build a set of Hunspell files (:file:`.aff` and :file:`.dic`) from data that
matches the specified criteria.

Syntax
======

To build Hunspell files, use the following syntax:

.. code:: bash

    python utils/build -l LANGUAGE [build options]

For example, to build the default Hunspell files of a language, use:

.. code:: bash

    python utils/build -l LANGUAGE

Or, if you want to build a specific preset of the specified language, use:

.. code:: bash

    python utils/build -l LANGUAGE -p PRESET

The resulting files are saved to a :file:`build` folder.

Use the following commands to get a list of available languages or a list of presets available for
the specified language:

.. code:: bash

    python utils/build --list-languages
    python utils/build -l LANGUAGE --list-presets

Finally, you can use the following command to get extended command-line help for this script:

.. code:: bash

    python utils/build -h


Basic Options
=============

-l LANGUAGE, --language=LANGUAGE
        Language code of the Hunspell files.

-o FILENAME, --output=FILENAME
        Name of the output file. For example, if FILENAME is :file:`myspellchecker`, output files
        are :file:`myspellchecker.aff` and :file:`myspellchecker.dic`. Default: LANGUAGE.

-f PATH, --output-folder=PATH
        Path of the folder where the output files are created. Default: :file:`./build`.

-p PRESET, --preset=PRESET
        Name of a spellchecker preset to build.

        Presets are named sets of data modules. Language data folders may contain a
        configuration file that defines one or more presets, which are sets of data modules of
        that language that are often build together by people building a spellchecker from
        sources for that language.

        Most languages provide a default preset which is used if you do not specify any preset
        or module filtering option.

--list-languages
        Lists all available language codes. Any other option is ignored.

--list-presets
        Lists all available presets for LANGUAGE. Any other option, excluding :code:`-l`, is
        ignored.

-h, --help
        Shows this command-line help. Any other option is ignored.


Module Filtering
================

The source data of the spellchecker is divided in modules, submodules, and so on, following a tree
hierarchy. If you have needs that module presets do not cover, you can use module filtering options
to specify which modules you want or do not want in your spellchecker.

Module filtering options allow you to specify which modules of the spellchecking data should make
its way into the output Hunspell files.

Specifying Modules
------------------

Module filtering options let you specify:

* A comma-separated list of module paths.
* :file:`*`, to indicate that you want to load all available modules.

You can specify any module filtering option more than once.


Module Search Paths
-------------------

Module paths must be relative to either of the following search paths:

* :file:`data/LANGUAGE/`, which contains Hunspell-specific data.
* :file:`external/spelling/data/LANGUAGE/`, which contains generic spelling data.

If you prepend a module path with :file:`common/`, the remaining path is relative to either
of the following search paths instead:

* :file:`data/common/`, which contains language-independent Hunspell-specific data.
* :file:`external/spelling/data/common/`, which contains generic language-independent spelling data.

The special :file:`*` module path is also affected by these rules:

* :file:`*` includes all modules for LANGUAGE, but it does not load any language-independent module.
* :file:`common/*` includes all language-independent modules, but it does not load any module for
  LANGUAGE.

Inclusion and Exclusion
-----------------------

Each filtering option to include modules has a counterpart option that allows you to exclude
previously-included modules. Regular filtering options also allow you to include
previously-excluded modules. So, for example, if you have the following folder tree in your search
paths:

* :file:`module1`
    * :file:`module1.1`
        * :file:`module1.1.1`
        * :file:`module1.1.2`
        * :file:`module1.1.3`
    * :file:`module1.2`
* :file:`module2`

On the command line you can pass parameters that do the following:

* Include :file:`*`.
* Exclude :file:`module1/module1.1`.
* Include :file:`module1/module1.1/module1.1.1`.

As a result, the following modules would be used to build a spellchecker: :file:`module1`,
:file:`module1.1.1`, :file:`module1.2`, :file:`module2`.


Module Filtering Options
------------------------

You may use any of the following filtering options:

-a MODULES, --aff=MODULES
        Modules of word-formation rules to load.

--exclude-aff=MODULES
        Modules of word-formation rules to exclude.

-d MODULES, --dic=MODULES
        Modules of word lists to load.

--exclude-dic=MODULES
        Modules of word lists to exclude.

-r MODULES, --rep=MODULES
        Modules of word replacement suggestion rules to load.

--exclude-rep=MODULES
        Modules of word replacement suggestion rules to exclude.
"""

import codecs, json, re, sys
from getopt import getopt, GetoptError
from os import listdir, makedirs, path, popen, sep, walk

from PyICU import Locale, Collator


def root_dir():
    return path.join(path.dirname(__file__), "..", "..")


def external_dir():
    return path.join(root_dir(), "external")


sys.path.append(path.join(external_dir(), "pydiomatic"))
from idiomatic.ui import warn_about_option_overwrite


def data_dir():
    return path.join(root_dir(), "data")


def lexicon_data_dir():
    return path.join(external_dir(), "lexicon", "data")


def spelling_data_dir():
    return path.join(external_dir(), "spelling", "data")


def lexion_extension():
    return u".lex.json"


def list_languages():
    folders = []
    for folder in listdir(data_dir()):
        if folder.strip(".") and folder != u"common":
            folders.append(folder)
    for folder in sorted(folders):
        print folder


def load_language_data(language):
    language_file_path = path.join(data_dir(), language, "language.json")
    with open(language_file_path, "rb") as fp:
        return json.load(fp)


def language_collator(language):
    return Collator.createInstance(Locale(language + ".UTF-8"))


def list_presets(language):
    presets = []
    language_data = load_language_data(language)
    if "presets" in language_data:
        collator = language_collator(language)
        for preset in sorted(language_data["presets"].keys(), cmp=collator.compare):
            print preset
            if "displayName" in language_data["presets"][preset]:
                print u" "*4 + language_data["presets"][preset]["displayName"]
            if "description" in language_data["presets"][preset]:
                print u" "*4 + language_data["presets"][preset]["description"]


def load_preset(name, language):
    preset = {}
    language_data = load_language_data(language)
    if "presets" in language_data:
        if name in language_data["presets"]:
            preset = language_data["presets"][name]
    return preset


def iter_module_folder_paths(folder, extension):
    for root_folder, folder_names, file_names in walk(folder):
        for file_name in file_names:
            if file_name.endswith(extension):
                yield path.join(root_folder, file_name)


def filter_to_modules(filter):
    if isinstance(filter, list):
        return filter
    else:
        return filter.split(u",")


def iter_module_paths(module_path, extension):

    # If with .<extension> it is a file, include the file.
    # Note: if both a <module> folder and a <module>.<extension> file exist, both are yield.
    module_file_path = u"{}.{}".format(module_path, extension)
    if path.isfile(module_file_path):
        yield module_file_path

    # If module is a folder, get all .<extension> files inside.
    if path.isdir(module_path):
        for file_path in iter_module_folder_paths(module_path, extension):
            yield file_path


def module_to_paths(module, language, extension):
    search_folder = language
    if module.startswith(u"common/"):
        search_folder = u"common"
        module = module[7:]
    search_paths = [path.join(data_dir(), search_folder),
                    path.join(spelling_data_dir(), search_folder)]
    path_batch = set()
    for search_path in search_paths:
        if module != u"*":
            search_path = path.join(search_path, module)
        for found_path in iter_module_paths(search_path, extension=extension):
            path_batch.add(found_path)
    return path_batch


def filters_to_paths(filters, language, extension):
    paths = set()
    for filter in filters:
        if isinstance(filter, list):
            filter_type, filter_string = filter
        else:
            filter_type = "include"
            filter_string = filter
        module_strings = filter_to_modules(filter_string)
        for module_string in module_strings:
            path_batch = module_to_paths(module_string, language=language, extension=extension)
            if filter_type == "include":
                paths = paths | path_batch
            else: # exclude
                paths = paths - path_batch
    return paths


def strip_comments(line):
    index = line.find('#')
    if index < 0:
        return line
    return line[0:index]


def simplify_spacing(line):
    line = line.replace('\t', ' ')
    line = re.sub(' +', ' ', line)
    return line


def strip_line(line):
    line = strip_comments(line)
    line = line.rstrip() + '\n'
    line = simplify_spacing(line)
    return line


def line_is_useless(line):
    strippedLine = line.strip()
    if strippedLine == "" or strippedLine[0] == "#":
        return True
    return False


def load_and_strip(file_path):
    parsed_content = u""
    with codecs.open(file_path, "r", "utf-8") as fp:
        for line in fp:
            if not line_is_useless(line):
                parsed_content += strip_line(line)
    return parsed_content


def load_files_and_strip(file_paths):
    content = u""
    for file_path in file_paths:
        content += load_and_strip(file_path)
    return content


def lines_to_rep(lines, language):
    content = u""
    if lines:
        content = u"REP {}\n".format(len(lines))
        collator = language_collator(language)
        for line in sorted(lines, cmp=collator.compare):
            content += u"REP {}\n".format(line)
    return content


def remove_duplicate_lines(lines):
    unique_lines = set()
    for line in lines:
        unique_lines.add(line)
    return unique_lines


def load_rep_lines(module_paths):
    unparsed_content = load_files_and_strip(module_paths)
    return remove_duplicate_lines(unparsed_content.splitlines())


def language_and_module_from_path(module_path):
    parts = module_path.split(sep)
    data_index = len(parts)-1
    while parts[data_index] != "data":
        data_index -= 1
    return parts[data_index+1], sep.join(parts[data_index+2:])


def load_word_data_from_file(word, file_path):
    with open(file_path, "rb") as fp:
        data = json.load(fp)
    if word in data:
        return data[word]
    return None


def load_word_data_from_file_if_exists(word, file_path):
    if path.exists(file_path):
        return load_word_data_from_file(word, file_path)
    return None


def load_word_data_from_folder(word, folder, skip=[]):
    for root_folder, folder_names, file_names in walk(folder):
        folder_names[:] = [d for d in folder_names if not
                            any(path.join(root_folder, d).startswith(searched_path)
                                for searched_path in skip)]
        for file_name in file_names:
            if file_name.endswith(lexion_extension()):
                module_path = path.join(root_folder, file_name)
                for searched_path in skip:
                    if module_path.startswith(folder):
                        continue
                data = load_word_data_from_file_if_exists(word, module_path)
                if data:
                    return data
    return None


def load_word_model(word, language, search_from=None):
    data_path = lexicon_data_dir()
    searched_paths = []
    if search_from:
        module_path = path.join(data_path, language, search_from + lexion_extension())
        data = load_word_data_from_file_if_exists(word, module_path)
        if data:
            return data
        searched_paths.append(module_path)
        breadcrumbs = search_from.split(sep)
        while breadcrumbs:
            search_path = path.join(data_path, language, sep.join(breadcrumbs))
            data = load_word_data_from_folder(word, search_path, skip=searched_paths)
            if data:
                return data
            searched_paths.append(search_path)
            breadcrumbs = breadcrumbs[:-1]
    search_path = path.join(data_path, language)
    data = load_word_data_from_folder(word, search_path, skip=searched_paths)
    if data:
        return data
    return None


def root_and_suffix_from_words(words):
    first_word = words[0]
    root = first_word
    first_word_suffix = u""
    for word in words[1:]:
        while not word.startswith(root):
            first_word_suffix = first_word[-len(first_word_suffix)+1:]
            root = root[:-1]
    return root, first_word_suffix


def apply_model_to_word(model, word, language):
    with open(path.join(lexicon_data_dir(), language, "word-models.json")) as fp:
        models = json.load(fp)
    if not model in models:
        return None
    model_data = models[model]
    applied_model = {
        "common": {
            "part-of-speech": model_data["common"]["part-of-speech"]
        }
    }
    if "categories" in model_data["common"]:
        applied_model["common"]["categories"] = model_data["common"]["categories"]
    if "inflected" in model_data:
        inflection = model_data["common"]["inflection"]
        with open(path.join(lexicon_data_dir(), language, "inflections.json")) as fp:
            inflections = json.load(fp)
        if not inflection in inflections:
            return None
        inflection_data = inflections[inflection]
        model_word_root, suffix = root_and_suffix_from_words(inflection_data)
        inflected_data = model_data["inflected"]
        index = 0
        applied_model["inflections"] = []
        while index < len(inflection_data):
            if len(suffix):
                inflected_word = word[:-len(suffix)] + inflection_data[index][len(model_word_root):]
            else:
                inflected_word = word + inflection_data[index][len(model_word_root):]
            categories = inflected_data[index]
            applied_model["inflections"].append([inflected_word, categories])
            index += 1
    else:
        applied_model["inflections"] = [[word, []]]
    return applied_model


def load_word_data(word, language, search_from=None):
    model = load_word_model(word, language=language, search_from=search_from)
    if not model:
        return None
    return apply_model_to_word(model, word, language=language)


def map_word_inflections(source_inflections, target_inflections):
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
                    mapping.append([source_inflection[0], target_inflection[0]])
    return mapping


def load_rep_json_lines(module_paths):
    lines = set()
    for module_path in module_paths:
        with open(module_path, "rb") as fp:
            data = json.load(fp)
        language, module = language_and_module_from_path(module_path)
        for source, target in data:
            source_data = load_word_data(source, language=language, search_from=module)
            target_data = load_word_data(target, language=language, search_from=module)
            mapping = map_word_inflections(source_data["inflections"], target_data["inflections"])
            for source_word, target_word in mapping:
                lines.add(u"^{}$ {}".format(source_word, target_word))
    return lines


def load_suggestion_rules(module_paths, language):
    lines = load_rep_lines(module_paths["rep"])
    lines = lines | load_rep_json_lines(module_paths["rep.json"])
    return lines_to_rep(lines, language=language)


def build_aff(module_paths, output_file_path, language):
    content = load_and_strip(path.join(data_dir(), language, u"base.aff"))
    content += load_files_and_strip(module_paths["aff"])
    content += load_suggestion_rules(module_paths, language=language)
    with codecs.open(output_file_path, "w", "utf-8") as fp:
        fp.write(content)


def lines_to_dic(lines, language):
    content = u""
    if lines:
        collator = language_collator(language)
        for line in sorted(lines, cmp=collator.compare):
            content += line + u"\n"
    return content


def load_dic(module_paths, language):
    unparsed_content = load_files_and_strip(module_paths)
    unique_lines = remove_duplicate_lines(unparsed_content.splitlines())
    return lines_to_dic(unique_lines, language=language)


def build_dic(module_paths, output_file_path, language):
    content = load_dic(module_paths["dic"], language=language)
    with codecs.open(output_file_path, "w", "utf-8") as fp:
        fp.write(content)


def build_files(module_paths, language, output_filename, output_folder):
    if not path.exists(output_folder):
        makedirs(output_folder)
    build_aff(module_paths, path.join(output_folder, output_filename + ".aff"), language=language)
    build_dic(module_paths, path.join(output_folder, output_filename + ".dic"), language=language)


def extension_to_content_type(extension):
    if extension == "rep.json":
        return "rep"
    else:
        return extension


def extend_module_paths_from_filters(module_paths, filters, language):
    for extension in module_paths.keys():
        type = extension_to_content_type(extension)
        module_paths[extension] = filters_to_paths(filters[type], language=language,
                                                   extension=extension)
    return module_paths


def main(argv):

    try:
        options, arguments = getopt(argv, "a:d:f:hl:o:p:r:", ["aff=", "dic=", "exclude-aff=",
            "exclude-dic=", "exclude-rep=", "help", "language=", "list-languages", "list-presets",
            "output=", "output-folder=", "preset=", "rep="])
    except GetoptError as error:
        print(error)
        sys.exit(2)

    language = None
    output_filename = None
    output_folder = None
    preset_name = None
    list_presets_option = False
    module_filters = { "aff": [], "dic": [], "rep": [] }
    module_paths = { "aff": [], "dic": [], "rep": [], "rep.json": [] }

    for option, value in options:
        if option in ("-l", "--language"):
            if language:
                warn_about_option_overwrite(option=option, previous_value=language, new_value=value)
            language = value
        elif option in ("-o", "--output"):
            if output_filename:
                warn_about_option_overwrite(option=option, previous_value=output_filename,
                                            new_value=value)
            output_filename = value
        elif option in ("-f", "--output-folder"):
            if output_folder:
                warn_about_option_overwrite(option=option, previous_value=output_folder,
                                            new_value=value)
            output_folder = value
        elif option in ("-p", "--preset"):
            if preset_name:
                warn_about_option_overwrite(option=option, previous_value=preset_name,
                                            new_value=value)
            preset_name = value
        elif option == "--list-languages":
            list_languages()
            sys.exit()
        elif option == "--list-presets":
            list_presets_option = True
        elif option in ("-h", "--help"):
            print(__doc__)
            sys.exit()

        elif option in ("-a", "--aff"):
            module_filters["aff"].append(["include", value])
        elif option == "--exclude-aff":
            module_filters["aff"].append(["exclude", value])
        elif option in ("-d", "--dic"):
            module_filters["dic"].append(["include", value])
        elif option == "--exclude-dic":
            module_filters["dic"].append(["exclude", value])
        elif option in ("-r", "--rep"):
            module_filters["rep"].append(["include", value])
        elif option == "--exclude-rep":
            module_filters["rep"].append(["exclude", value])

        else:
            assert False, "unhandled option"

    if not language:
        print(u"Error: You did not specify a language code, " \
              u"nor any option that does not require one.")
        sys.exit(2)
    elif not path.exists(path.join(data_dir(), language)):
        print(u"Error: You specified an unsupported language code, ‘{language}’. " \
              u"There is no subfolder in the ‘data’ folder named ‘{language}’. " \
              u"Use the ‘--list-languages’ option to get a list of supported languages.".format(
                  language=language))
        sys.exit(2)

    if not output_filename:
        output_filename = language

    if not output_folder:
        output_folder = u"build"

    if list_presets_option:
        list_presets(language)
        sys.exit()

    if preset_name:
        preset = load_preset(preset_name, language)
        if not preset:
            print(u"Error: The specified preset, ‘{}’, " \
                  u"is not valid for language ‘{}’.".format(preset_name, language))
            print(u"Valid presets for ‘{}’:".format(language))
            list_presets(language)
            sys.exit(2)
        else:
            if any(value for key, value in module_filters.iteritems()):
                print(u"Warning: You have specified a preset: ‘{}’. " \
                      u"Module filtering options are ignored.".format(preset_name))
            module_paths = extend_module_paths_from_filters(module_paths, preset,
                                                            language=language)
    else:
        if any(filters for module_extension, filters in module_filters.iteritems()):
            module_paths = extend_module_paths_from_filters(module_paths, module_filters,
                                                            language=language)
        else:
            language_data = load_language_data(language)
            for code, preset in language_data["presets"].iteritems():
                if "default" in preset and preset["default"]:
                    module_paths = extend_module_paths_from_filters(module_paths, preset,
                                                                    language=language)
                    break

    build_files(module_paths=module_paths, language=language, output_filename=output_filename,
                output_folder=output_folder)


if __name__ == "__main__":
    main(sys.argv[1:])
