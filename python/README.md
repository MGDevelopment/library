Python Modules for Tematika.com
===============================

This repository contains all the libraries and modules required by the rest of
the applications running tematika.com

Modules
-------

### ecommerce

This module contain packages providing basic methods for managing the
front-end application mostly involving generation of content.

### ecommerce.config

This package provides an interface to load and access configuration specific
to the current instance.

### ecommerce.db

This package provides a basic access interface to the content database.

### ecommerce.content

This package provides basic methods for content generation using templates.

Usage
-----

To generate install packages ready for distribution run:

        $ python setup.py sdist

The packages will be ready inside a directory named dist 

To run tests:

        $ python setup.py test

To run clean up:

        $ python setup.py clean

