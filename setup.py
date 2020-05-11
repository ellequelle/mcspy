import setuptools
from setuptools import find_packages

# Load the __version__ variable without importing the package already
exec(open('mcspy/version.py').read())

install_requires = ['numpy >= 1.18',
                    'pandas >= 1.0',
                    'requests >= 2.23']

setuptools.setup(
    name='mcspy-ellequelle',
    version=__version__,
    author='Elle Hanson',
    author_email='elleh3113@gmail.com',
    description='',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ellequelle/mcspy',
    install_requires=install_requires,
    license='Apache-2',
    platforms='any',
    packages=find_packages(include=['mcspy']),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
        'Topic :: Scientific/Engineering :: Astronomy',
        'Topic :: Scientific/Engineering :: Physics',
        "Operating System :: OS Independent",
        ],
    keywords='Mars Reconnaisance Orbiter Climate Sounder atmospheric radiative transfer PDS MCS planetary data system',
    entry_points={'console_scripts':['']},
    python_requires='>=3.7',
)
