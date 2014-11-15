The Language File
=================

This topic explains the keys of the :file:`language.json` file that you can
define in this repository. For general information about this file, see the
`Pydiomatic documentation for the language file`_.

.. _Pydiomatic documentation for the language file: http://pydiomatic.readthedocs.org/en/latest/api/data.html#the-language-file

Presets
-------

The object of a preset in this repository may contain any of the following
fields:

:aff:
    List of modules of word-formation rules to load.

:dic:
    List of modules of word lists to load.

:rep:
    List of modules of word replacement suggestion rules to load.

See the `Pydiomatic documentation for modules`_ to learn how to specify the
values of these lists.

.. _Pydiomatic documentation for modules: http://pydiomatic.readthedocs.org/en/latest/api/data.html#modules


Example
-------

The following is a real-life example of a :file:`language.json` file of this
repository:

.. literalinclude:: /../data/gl/language.json


.. _JSON: http://json.org/
.. _