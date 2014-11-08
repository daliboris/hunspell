#!/usr/bin/env python2
# -*- coding:utf-8 -*-

"""Build a set of Hunspell spellchecking files.

Run this script to build a set of Hunspell files (:file:`.aff` and
:file:`.dic`) from data that matches the specified criteria.

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

Use the following commands to get a list of available languages or a list of
presets available for the specified language:

.. code:: bash

    python utils/build --list-languages
    python utils/build -l LANGUAGE --list-presets

Finally, you can use the following command to get extended command-line help
for this script:

.. code:: bash

    python utils/build -h


Basic Options
=============

-l LANGUAGE, --language=LANGUAGE
        Language code of the Hunspell files.

-o FILENAME, --output=FILENAME
        Name of the output file. For example, if FILENAME is
        :file:`myspellchecker`, output files are :file:`myspellchecker.aff` and
        :file:`myspellchecker.dic`. Default: LANGUAGE.

-f PATH, --output-folder=PATH
        Path of the folder where the output files are created. Default:
        :file:`./build`.

-p PRESET, --preset=PRESET
        Name of a spellchecker preset to build.

        Presets are named sets of data modules. Language data folders may
        contain a
        configuration file that defines one or more presets, which are sets of
        data modules of that language that are often build together by people
        building a spellchecker from sources for that language.

        Most languages provide a default preset which is used if you do not
        specify any preset or module filtering option.

--list-languages
        Lists all available language codes. Any other option is ignored.

--list-presets
        Lists all available presets for LANGUAGE. Any other option, excluding
        :code:`-l`, is ignored.

-h, --help
        Shows this command-line help. Any other option is ignored.


Module Filtering Options
========================

You may use any of the following `module filtering options`_:

.. _module filtering options: http://pydiomatic.rtfd.org/en/latest/data.html

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

from getopt import getopt, GetoptError
from os import path
import sys


def _root_dir():
    return path.join(path.dirname(__file__), "..")

root_path = _root_dir()
if root_path not in sys.path:
    sys.path.insert(0, path.join(root_path))


from hunspell import data_dirs


def _external_dir():
    return path.join(_root_dir(), "external")


sys.path.append(path.join(_external_dir(), "pydiomatic"))
from idiomatic.data import load_presets
from idiomatic.ui import \
    error_and_exit_if_unsupported_language, \
    list_languages, \
    list_presets, \
    load_preset_or_error_and_exit, \
    missing_language_error_and_exit, \
    warn_about_option_overwrite, \
    warn_if_preset_and_filters
from hunspell import build_files, module_paths_from_filters


def _main(argv):

    try:
        options, arguments = getopt(
            argv,
            "a:d:f:hl:o:p:r:",
            ["aff=", "dic=", "exclude-aff=", "exclude-dic=", "exclude-rep=",
             "help", "language=", "list-languages", "list-presets", "output=",
             "output-folder=", "preset=", "rep="])
    except GetoptError as error:
        print(error)
        sys.exit(2)

    language = None
    output_file_name = None
    output_folder = None
    preset_name = None
    list_presets_option = False
    module_filters = {"aff": [], "dic": [], "rep": []}

    for option, value in options:
        value = value.decode("utf-8")
        if option in ("-l", "--language"):
            if language:
                warn_about_option_overwrite(option=option,
                                            previous_value=language,
                                            new_value=value)
            language = value
        elif option in ("-o", "--output"):
            if output_file_name:
                warn_about_option_overwrite(option=option,
                                            previous_value=output_file_name,
                                            new_value=value)
            output_file_name = value
        elif option in ("-f", "--output-folder"):
            if output_folder:
                warn_about_option_overwrite(option=option,
                                            previous_value=output_folder,
                                            new_value=value)
            output_folder = value
        elif option in ("-p", "--preset"):
            if preset_name:
                warn_about_option_overwrite(option=option,
                                            previous_value=preset_name,
                                            new_value=value)
            preset_name = value
        elif option == "--list-languages":
            list_languages(data_dirs())
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
        missing_language_error_and_exit()
    else:
        error_and_exit_if_unsupported_language(language, data_dirs=data_dirs())

    if not output_file_name:
        output_file_name = language

    if not output_folder:
        output_folder = u"build"

    if list_presets_option:
        list_presets(language, data_dirs())
        sys.exit()

    if preset_name:
        preset = load_preset_or_error_and_exit(preset_name, language,
                                               data_dirs())
        warn_if_preset_and_filters(preset_name, module_filters)
        module_paths = module_paths_from_filters(preset, language=language)
    else:
        if any(filters for module_extension, filters in
               module_filters.iteritems()):
            module_paths = module_paths_from_filters(module_filters,
                                                     language=language)
        else:
            for code, preset in load_presets(
                    language, data_dirs()).iteritems():
                if "default" in preset and preset["default"]:
                    module_paths = module_paths_from_filters(preset,
                                                             language=language)
                    break

    build_files(module_paths=module_paths, language=language,
                output_file_name=output_file_name, output_folder=output_folder)


if __name__ == "__main__":
    _main(sys.argv[1:])
