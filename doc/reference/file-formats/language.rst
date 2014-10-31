The Language File
=================

The :file:`language.json` file is a `JSON`_ file that provides a JSON object with information about
a language and its spellchecking data.

Presets
-------

The :file:`language.json` of a language may define a set of presents, named groups of modules. When
you use the :doc:`build </reference/tools/build>` tool to generate Hunspell files, instead of
specifying your own group of desired modules on the command line, you may specify the name of a
preset instead to build the modules of the preset into Hunspell files.

The main JSON object of :file:`language.json` may contain a :code:`presets` key with another object
as value.

.. code:: json

    {
        "presets": {}
    }

Each key in the :code:`presets` object is the name of a preset, the name that you can pass to the
:doc:`build </reference/tools/build>` tool if you want to generate the Hunspell files for the
modules of that preset. The key points to an object that holds all the information about the preset.

.. code:: json

    {
        "preset1": {},
        "preset2": {},
        "presetN": {}
    }

The object of a preset may contain any of the following fields:

:default:
    Whether the preset is the default preset (:code:`true`) or not (:code:`false`). You should only
    define this key in one preset object, with value :code:`true`. There is no need to use the key
    on any other preset object.

    Default value: :code:`false`

:displayName:
    Optional display name of the preset.

    This field should be written using the language of the folder where :file:`languages.json` is
    stored.

:description:
    Optional description of the preset.

    This field should be written using the language of the folder where :file:`languages.json` is
    stored.

:aff:
    List of modules of word-formation rules to load.

:dic:
    List of modules of word lists to load.

:rep:
    List of modules of word replacement suggestion rules to load.

Lists of modules may be specified in two different ways. If you only need to specify a list of
modules to include, you can provide that list directly:

.. code:: json

    {
        "aff": ["module1", "module2/module2.1/module2.1.5"]
    }

In some complex situations, however, you might end up with quite a long list. For example, imagine
that you want all modules in your language, 100 or more modules, except for one of them. In cases
like this one, you can specify a list of lists, where each list has two items:

* A type of filter, which is a string, either :code:`"include"` or :code:`exclude`.
* A list of modules to filter.

This way you can specify a secuence of module inclusion and exclusion. For example:

.. code:: json

    {
        "aff": [["include", ["*"]], ["exclude", ["badmodule1", "badmodule2"]]]
    }


Example
-------

The following is a real-life example of a :file:`language.json` file:

.. literalinclude:: /../data/gl/language.json


.. _JSON: http://json.org/
.. _