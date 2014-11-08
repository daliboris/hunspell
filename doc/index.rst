Hunspell
========

**Hunspell** is a repository that contains spellchecking data and tools to
easily build `Hunspell`_ spellchecking files (:file:`.aff` and :file:`.dic`)
for different languages.

The repository contains:

* Spellchecking data (words, inflection rules, and replacement suggestions),
  distributed in a tree of modules.
* A tool to build a set of modules of spellchecking data into Hunspell files.
* A framework for contributors to write Python modules that can generate
  modules of spellchecking data from external sources.

Most Hunspell spellchecking files are developed the same way that they are
distributed: all rules and words are edited directly on the :file:`.aff` and
:file:`.dic` files. But different people might have different spellchecking
needs. People working on a field such as biomechanics or chemistry might want
their spellcheckers to understand some field-specific vocabulary, while other
people might want to have a spellchecker that only accepts the vocabulary found
in a specific online dictionary, and provide suggestions to replace any word
that the online dictionary does not consider valid.

To solve that problem, we keep spellchecking data in separate modules. This
allows us to easily build different spellcheckers from a single database,
combining different modules as we see fit. For example, the repository lets you
build:

* A spellchecker that includes words from a known online dictionary plus names
  of people extracted from the Wikipedia.
* A spellchecker that includes words from several different dictionaries.
* A spellchecker that includes words specific to one or more fields, such as
  biology or computing.


Table of Contents
=================

.. toctree::
   :maxdepth: 2

   quick-start-guide
   reference/index


Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _Hunspell: http://hunspell.sourceforge.net/
