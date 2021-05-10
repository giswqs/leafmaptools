============
leafmaptools
============

.. image:: https://mybinder.org/badge_logo.svg
        :target: https://mybinder.org/v2/gh/giswqs/leafmaptools/master?urlpath=lab/tree/examples/notebooks

.. image:: https://img.shields.io/pypi/v/leafmaptools.svg
        :target: https://pypi.python.org/pypi/leafmaptools

.. image:: https://img.shields.io/conda/vn/conda-forge/leafmaptools.svg
        :target: https://anaconda.org/conda-forge/leafmaptools

.. image:: https://pepy.tech/badge/leafmaptools
        :target: https://pepy.tech/project/leafmaptools

.. image:: https://github.com/giswqs/leafmaptools/workflows/docs/badge.svg
        :target: https://leafmaptools.gishub.org

.. image:: https://github.com/giswqs/leafmaptools/workflows/build/badge.svg
        :target: https://github.com/giswqs/leafmaptools/actions?query=workflow%3Abuild

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
        :target: https://opensource.org/licenses/MIT


**A Python package for building a tool widgets infrastructure with ipyleaflet and ipywidgets.**

-   Free software: MIT license
-   Documentation: https://leafmaptools.gishub.org
    

**Contents**

- `Introduction`_
- `Features`_
- `Installation`_
- `Examples`_
- `Credits`_


Introduction
------------

This is a Python package exploring ideas for building a tool widgets infrastructure with ipyleaflet and ipywidgets. The outcome should be a collection of useful and reusable tools that provide workarounds for missing features and can be used on and off the map without the need for writing Javascript code.


Features
--------

The Wiki contains some early [feature ideas](https://github.com/giswqs/leafmaptools/wiki/Feature-ideas) which can be used/imported from the code now. The following image is a sneak preview, more is about to come:

.. image:: https://github.com/giswqs/leafmaptools/raw/master/prototypes/prototype1.gif
        :target: https://github.com/giswqs/leafmaptools/raw/master/prototypes/prototype1.gifwGjpjh9IQ5I


Installation
------------

**leafmaptools** is available on `PyPI <https://pypi.org/project/leafmaptools/>`__. To install **leafmaptools**, run this command in your terminal:

.. code:: python

  pip install leafmaptools


**leafmaptools** is also available on `conda-forge <https://anaconda.org/conda-forge/leafmaptools>`__. If you have `Anaconda <https://www.anaconda.com/distribution/#download-section>`__ or `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`__ installed on your computer, you can create a conda Python environment to install leafmaptools:

.. code:: python

  conda create -n lmt python
  conda activate lmt
  conda install mamba -c conda-forge
  mamba install leafmaptools -c conda-forge 

Optionally, you can install `Jupyter notebook extensions <https://github.com/ipython-contrib/jupyter_contrib_nbextensions>`__, which can improve your productivity in the notebook environment. Some useful extensions include Table of Contents, Gist-it, Autopep8, Variable Inspector, etc. See this `post <https://towardsdatascience.com/jupyter-notebook-extensions-517fa69d2231>`__ for more information.       

.. code:: python

  mamba install jupyter_contrib_nbextensions -c conda-forge 


If you have installed **leafmaptools** before and want to upgrade to the latest version, you can run the following command in your terminal:

.. code:: python

  pip install -U leafmaptools


If you use conda, you can update leafmaptools to the latest version by running the following command in your terminal:
  
.. code:: python

  mamba update -c conda-forge leafmaptools


To install the development version from GitHub using `Git <https://git-scm.com/>`__, run the following command in your terminal:

.. code:: python

  pip install git+https://github.com/giswqs/leafmaptools


Examples
--------

Example notebooks can be found in the docs/notebooks/examples folder. The easiest way to run these online without installing anything is to click the "launch binder" button above which will launch a pre-built Docker image and present all example notebooks which can be conveniently run online.  


Credits
-------

This package was created with `Cookiecutter <https://github.com/cookiecutter/cookiecutter>`__ and the `giswqs/pypackage <https://github.com/giswqs/pypackage>`__ project template.
