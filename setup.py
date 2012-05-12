"""
Example build script and use of a Cython module with Panda3D's C++ API
By Craig Macomber
"""

import sys
import os

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

# make setup do what we want,
# build extension modules in place
sys.argv.append('build_ext')
sys.argv.append('--inplace')

args={}

# configure OS dependant compiler settings
# you may need to adjust the paths to match your systems
libs=['libpanda']
args['library_dirs']=['/usr/lib64/panda3d']
args['include_dirs']=['/usr/include/panda3d', '/usr/include/bullet']
args['libraries']=['p3framework', 'panda', 'pandafx', 'pandaexpress', 'p3dtoolconfig', 'p3dtool', 'p3pystub', 'p3direct']


# use distutils to build the module
setup(
    name = 'path',
    ext_modules=[ 
    Extension("gravbot.ai.path", 
              sources=["gravbot/ai/path.pyx"],
              language="c++",
              **args
              ),
    ],
    cmdclass = {'build_ext': build_ext},
)


from panda3d.core import Vec3
print "Importing module"
import path 
