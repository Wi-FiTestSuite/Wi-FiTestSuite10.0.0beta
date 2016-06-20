# Script to convert python source to EXE
from distutils.core import setup
import py2exe
import sys
import os

pkg='wts.py'

setup(console=[pkg])
