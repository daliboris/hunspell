#!/usr/bin/env python2
# -*- coding:utf-8 -*-

"""Build a file of words (one word per line) that a set of Hunspell files
(:file:`.aff` and :file:`.dic`) accept.

Performance
===========

This script is much slower than Hunspell’s `unmunch`_ or `unmunch.sh`_.
Instead, it focuses on accuracy and maintainability (the source code is easy to
read, being Python).

If Hunspell’s existing solutions work for you, you are encouraged to use them
instead of using this script; that will save you time. However, you might want
to compare the output of Hunspell’s tools with the output of this script, just
in case Hunspell’s solutions are not working properly for your Hunspell files
and you simply did not notice yet.

.. _unmunch: http://hunspell.cvs.sourceforge.net/viewvc/hunspell/hunspell/src/\
tools/unmunch.c?view=markup
.. _unmunch.sh: http://sourceforge.net/projects/hunspell/files/Hunspell/1.2.8/\
unmunch.sh/download


Uncomplete Implementation
=========================

This script was coded for a specific set of two files, and not all features
of Hunspell were implemented. Missing features are, for example, support
for letter flags, for prefixes or for compound rules (compound rules
without * or + in them could be supported in theory). UTF-8 encoding is
assumed (and checked, the script stops for other encodings).

This script is also meant to run on files generated by the build tool of
this repository, which implies that single spacing is used, there are no
empty lines and there are no source comments.

However, I’m open to implement any feature that you need, including
corner-case features that would need to be optional (enabled through
command-line switches). Feel free to `ask for whatever you need`_.

.. _ask for whatever you need: https://github.com/eitsl/hunspell/issues


Syntax
======

To unmunch a set of Hunspell files, use the following syntax:

.. code:: bash

    python utils/unmunch.py -a <.aff file> -d <.dic file> [options]

The result is printed on the standard output. You may also specify an output
file:

.. code:: bash

    python utils/unmunch.py -a <.aff file> -d <.dic file> -o <output file> \
[options]

Finally, you can use the following command to get extended command-line help
for this script:

.. code:: bash

    python utils/utils.py -h


Options
=======

-a FILE, --aff=FILE
        Affixes (:file:`.aff`) file.

-d FILE, --dic=FILE
        Dictionary (:file:`.dic`) file.

-o FILE, --output=FILE
        Path to the output file. If you omit this parameter, the results are
        printed on the standard output.

-h, --help
        Shows this command-line help. Any other option is ignored.
"""

from getopt import getopt, GetoptError
from os import path
import sys


def _root_dir():
    return path.join(path.dirname(__file__), "..")

root_path = _root_dir()
if root_path not in sys.path:
    sys.path.insert(0, path.join(root_path))


from hunspell import unmunch_files


def _external_dir():
    return path.join(_root_dir(), "external")


sys.path.append(path.join(_external_dir(), "pydiomatic"))
from idiomatic.ui import \
    warn_about_option_overwrite


def _main(argv):

    try:
        options, arguments = getopt(argv, "a:d:ho:",
                                    ["aff=", "dic=", "help", "output="])
    except GetoptError as error:
        print(error)
        sys.exit(2)

    aff_path = None
    dic_path = None
    output_path = None

    for option, value in options:
        value = value.decode("utf-8")
        if option in ("-a", "--aff"):
            if aff_path:
                warn_about_option_overwrite(option=option,
                                            previous_value=aff_path,
                                            new_value=value)
            aff_path = value
        elif option in ("-d", "--dic"):
            if dic_path:
                warn_about_option_overwrite(option=option,
                                            previous_value=dic_path,
                                            new_value=value)
            dic_path = value
        elif option in ("-o", "--output"):
            if output_path:
                warn_about_option_overwrite(option=option,
                                            previous_value=output_path,
                                            new_value=value)
            output_path = value
        elif option in ("-h", "--help"):
            print(__doc__)
            sys.exit()
        else:
            print(u"Error: unexpected option: ‘{}’. "
                  u"Use ‘-h’ for help.".format(option))
            sys.exit(2)

    if not aff_path:
        print(u"You must specify an ‘.aff’ file "
              u"using the ‘-a’ command-line switch.")
        sys.exit(2)
    aff_path = path.abspath(aff_path)

    if not dic_path:
        print(u"You must specify a ‘.dic’ file "
              u"using the ‘-d’ command-line switch.")
        sys.exit(2)
    dic_path = path.abspath(dic_path)

    if output_path:
        output_path = path.abspath(output_path)

    unmunch_files(aff_path=aff_path, dic_path=dic_path,
                  output_path=output_path)


if __name__ == "__main__":
    _main(sys.argv[1:])
