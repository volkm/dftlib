***********************
Installation
***********************

Installation Steps
====================

Virtual Environments
--------------------

Virtual environments create isolated environments for your projects.
This helps to keep your system clean, work with different versions of packages and different version of python.
While it is not required, we recommend the use of such virtual environments. To get you started, we recommend
`this guide <https://docs.python-guide.org/en/latest/dev/virtualenvs/>`_ or
`this primer <https://realpython.com/blog/python/python-virtual-environments-a-primer>`_.

In short you can create a virtual environment ``env`` with::

	$ pip install virtualenv
	$ virtualenv -p python3 env
	$ source env/bin/activate

The last step activates the virtual environment.
Whenever using the environment, the console prompt is prefixed with ``(env)``.


Installing dftlib
-----------------

You can simply install dftlib via its pypi package::

	$ pip install dftlib

To install dftlib with support for the DFT analysis via the `Storm modelchecker <https://www.stormchecker.org>`_ install the optional stormpy dependency::

	$ pip install dftlib[stormpy]


Building dftlib documentation
------------------------------

To build this documentation, you need additional Python dependencies as well as `pandoc <https://pandoc.org/>`_.
You can install the required python dependencies automatically with::

	$ pip install .[doc]

Then build the documentation::

	$ cd doc
	$ make html
