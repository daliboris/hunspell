Quick Start Guide
=================

Lets say that you want to build the latest version of the default spellchecker for Galician (language code: gl) from the repository. You simply need to follow these steps:

    1. `Grab our Github repository`_.
    2. Open the downloaded folder on a terminal.
    3. Run :code:`python utils/build.py -l gl`.

On a GNU/Linux terminal you can easily perform those steps running the following commands:

.. code:: bash

    git clone https://github.com/eitsl/hunspell.git
    cd hunspell/
    python utils/build.py -l gl

The :doc:`build </reference/tools/build>` tool generates a :file:`build` folder. Inside the :file:`build` folder you can find a set of Hunspell files: :file:`gl.aff` and :file:`gl.dic`.

That’s it! Check the `Hunspell command-line documentation`_ to learn how to use those two files.


.. _Grab our Github repository: https://help.github.com/articles/fetching-a-remote/#clone
.. _Hunspell command-line documentation: http://downloads.sourceforge.net/project/hunspell/Hunspell/Documentation/hunspell1.pdf