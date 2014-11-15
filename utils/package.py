#!/usr/bin/env python2
# -*- coding:utf-8 -*-

"""Build a set of Hunspell spellchecking files and package them.

Run this script to build a set of Hunspell files (:file:`.aff` and
:file:`.dic`) from a preset and package them along with information files.

Syntax
======

To package Hunspell files, use the following syntax:

.. code:: bash

    python utils/build -l LANGUAGE [options]

For example, to package all the presets of a language, use:

.. code:: bash

    python utils/build -l LANGUAGE

Or, if you want to package a specific preset, use:

.. code:: bash

    python utils/build -l LANGUAGE -p PRESET

The resulting archive is saved to a :file:`build` folder.

You may use the :code:`-v` switch to define the version of the package, and the
:code:`-n` switch to define the filename of the Hunspell files within the
package archive. For example:

.. code:: bash

    python utils/build -l gl -p drag -v 1.0 -o gl_ES

Use the following commands to get a list of available languages or a list of
presets available for the specified language:

.. code:: bash

    python utils/build --list-languages
    python utils/build -l LANGUAGE --list-presets

Finally, you can use the following command to get extended command-line help
for this script:

.. code:: bash

    python utils/build -h


Options
=======

-l LANGUAGE, --language=LANGUAGE
        Language code of the Hunspell files.

-p PRESET, --preset=PRESET
        Name of a spellchecker preset to build.

        Presets are named sets of data modules. Language data folders may
        contain a
        configuration file that defines one or more presets, which are sets of
        data modules of that language that are often build together by people
        building a spellchecker from sources for that language.

        Most languages provide a default preset which is used if you do not
        specify any preset or module filtering option.

-v VERSION, --version=VERSION
        VERSION is the version of the output archive. Default:
        Current date in format :code:`YYYYMMDD`; for example: :code:`20141109`.

-o FILENAME, --output-file=FILENAME
        Name of the output Hunspell files. For example, if FILENAME is
        :file:`myspellchecker`, output files are :file:`myspellchecker.aff` and
        :file:`myspellchecker.dic`. Default: :code:`LANGUAGE`.

-f PATH, --output-folder=PATH
        Path of the folder where the output archive is created. Default:
        :file:`./build`.

--list-languages
        Lists all available language codes. Any other option is ignored.

--list-presets
        Lists all available presets for LANGUAGE. Any other option, excluding
        :code:`-l`, is ignored.

-h, --help
        Shows this command-line help. Any other option is ignored.
"""

from getopt import getopt, GetoptError
from os import path, walk
import sys


def _root_dir():
    return path.join(path.dirname(__file__), "..")

root_path = _root_dir()
if root_path not in sys.path:
    sys.path.insert(0, path.join(root_path))


from hunspell import data_dir, data_dirs


def _external_dir():
    return path.join(_root_dir(), "external")


sys.path.append(path.join(_external_dir(), "pydiomatic"))
from idiomatic.data import load_presets
from idiomatic.languages import collator
from idiomatic.ui import \
    error_and_exit_if_unsupported_language, \
    list_languages, \
    list_presets, \
    load_preset_or_error_and_exit, \
    missing_language_error_and_exit, \
    warn_about_option_overwrite
from hunspell import build_files, module_paths_from_filters


def _main(argv):

    try:
        options, arguments = getopt(
            argv,
            "f:hl:o:p:v:",
            ["help", "language=", "list-languages", "list-presets",
             "output-file=", "output-folder=", "preset=", "version="])
    except GetoptError as error:
        print(error)
        sys.exit(2)

    language = None
    list_presets_option = False
    output_file_name = None
    output_folder = None
    preset_name = None
    version = None

    for option, value in options:
        value = value.decode("utf-8")
        if option in ("-l", "--language"):
            if language:
                warn_about_option_overwrite(option=option,
                                            previous_value=language,
                                            new_value=value)
            language = value
        elif option in ("-o", "--output-file"):
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
        elif option in ("-v", "--version"):
            if version:
                warn_about_option_overwrite(option=option,
                                            previous_value=version,
                                            new_value=value)
            version = value
        elif option == "--list-languages":
            list_languages(data_dirs())
            sys.exit()
        elif option == "--list-presets":
            list_presets_option = True
        elif option in ("-h", "--help"):
            print(__doc__)
            sys.exit()

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

    if not version:
        from time import strftime
        version = strftime("%Y%m%d")

    if list_presets_option:
        list_presets(language, data_dirs())
        sys.exit()

    presets = {}

    if preset_name:
        preset = load_preset_or_error_and_exit(preset_name, language,
                                               data_dirs())
        presets[preset_name] = preset
    else:
        for code, preset in load_presets(language, data_dirs()).iteritems():
            presets[code] = preset

    from os import makedirs
    from shutil import copy, move, rmtree
    from subprocess import call
    from tempfile import mkdtemp

    if not path.exists(output_folder):
        makedirs(output_folder)

    for preset_name in sorted(presets.keys(), cmp=collator(language).compare):

        output_archive_name = u"hunspell-{}-{}-{}.tar.xz".format(
            language, preset_name, version)

        print(u"• Packaging ‘{}’…".format(output_archive_name))

        temporary_folder = mkdtemp(prefix=u"hunspell")

        module_paths = module_paths_from_filters(presets[preset_name],
                                                 language=language)
        build_files(module_paths=module_paths, language=language,
                    output_file_name=output_file_name,
                    output_folder=temporary_folder)

        root, folders, files = next(walk(path.join(data_dir(), language)))
        for file_name in files:
            if file_name not in [u"language.hunspell", u"language.json"]:
                copy(path.join(root, file_name),
                     path.join(temporary_folder, file_name))

        call(u"tar -caf {} *".format(
            output_archive_name), shell=True, cwd=temporary_folder)

        move(path.join(temporary_folder, output_archive_name),
             path.join(output_folder, output_archive_name))

        rmtree(temporary_folder)


if __name__ == "__main__":
    _main(sys.argv[1:])
