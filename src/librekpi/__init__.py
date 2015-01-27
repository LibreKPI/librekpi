"""LibreKPI: the freedom of knowledge

This is a main package of a web-app
"""

from os.path import dirname, realpath

__author__ = 'Sviatoslav Sydorenko'
__email__ = 'svyatoslav@sydorenko.org.ua'
__date__ = '2015-01-14'
__appname__ = 'LibreKPI'
__version__ = '0.1'
__config__ = 'app.yaml'  # and environment variables (mostly for production)

SRC_DIR = dirname(realpath(__file__))
PRJ_ROOT = dirname(dirname(SRC_DIR))
