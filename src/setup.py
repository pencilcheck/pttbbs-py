from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [Extension("mbbsd", ["mbbsd.pyx"])]

setup(
  name = 'ptt BBS server',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)

