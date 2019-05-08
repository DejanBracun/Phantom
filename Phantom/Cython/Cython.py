import setuptools  # important
from distutils.core import setup
from Cython.Build import cythonize
setup(ext_modules = cythonize('C:\\Users\\Dejan\\Source\\Repos\\Phantom\\Phantom\\Cython\\example_cython.pyx'))
