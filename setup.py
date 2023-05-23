from setuptools import setup, find_packages

version = '0.1.0'

setup(
    name="arches-templating",
    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # http://packaging.python.org/en/latest/tutorial.html#version
    version=version,
    description="Arches templating provides an extensible templating engine for various file types",
    url="http://archesproject.org/",
    author="Farallon Geographics, Inc",
    author_email="dev@fargeo.com",
    license="GNU AGPL3",
    install_requires=[
        'Django >= 3.2.18',
        'python-pptx >= 0.6.21',
        'python-docx >= 0.8.11',
        'openpyxl >= 3.0.7'
    ],
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Information Technology",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Framework :: Django :: 1.11",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    # What does your project relate to?
    keywords="django arches cultural heritage",
    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite="tests.run_tests.run_all",
)
