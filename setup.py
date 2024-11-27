from setuptools import setup
from Cython.Build import cythonize

setup(ext_modules=cythonize('/data/yubei/Biotech/app/menu/__init__.py'))
