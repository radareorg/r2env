# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name="r2env",
    version="0.2.0",
    description="radare2 environment management tool",
    long_description="Easily install multiple versions of r2 and its plugins from source or binary on any platform",
    long_description_content_type="text/markdown",
    author="Radare2 Developers",
    author_email="pancake@nopcode.org",
    url="https://www.radare.org",
    install_requires=[
	"dploy>=0.1.2"
    ],
    license="MIT",
    zip_safe=True,
    keywords="reversing radare2 package version installation",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: JavaScript",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    packages=['r2env', 'r2env.db'],
    entry_points={
        'console_scripts': [
            "r2env = r2env.repl:main"
        ]
    }
)

