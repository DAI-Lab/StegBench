<p align="left">
<img width=15% src="https://dai.lids.mit.edu/wp-content/uploads/2018/06/Logo_DAI_highres.png" alt=“DAI-Lab” />
<i>An open source project from Data to AI Lab at MIT.</i>
</p>

<!-- Uncomment these lines after releasing the package to PyPI for version and downloads badges -->
<!--[![PyPI Shield](https://img.shields.io/pypi/v/stegtest.svg)](https://pypi.python.org/pypi/stegtest)-->
<!--[![Downloads](https://pepy.tech/badge/stegtest)](https://pepy.tech/project/stegtest)-->
[![Travis CI Shield](https://travis-ci.org/DAI-Lab/stegtest.svg?branch=master)](https://travis-ci.org/DAI-Lab/stegtest)
[![Coverage Status](https://codecov.io/gh/DAI-Lab/stegtest/branch/master/graph/badge.svg)](https://codecov.io/gh/DAI-Lab/stegtest)

# StegTest

This package allows autotesting of different datasets, steganographers, and steganalyzers. Using this package, extensive and thorough experiments can be carried out efficiently for a number of algorithms. Example configuration files are included as well as sample demo results. For quick-start, please refer to the manual below. 

- Documentation: https://DAI-Lab.github.io/stegtest
- Homepage: https://github.com/DAI-Lab/stegtest

# Overview

StegTest is a steganography orchestration package for the evaluation of both steganaographic and steganalysis methods. The system orchestrates extensive experimentation of steganographic procedures through the use of short, easy-to-use configuration files. 

# Install

## Requirements

**StegTest** has been developed and tested on [Python3.4, 3.5, 3.6 and 3.7](https://www.python.org/downloads/)

Also, although it is not strictly required, the usage of a [virtualenv](https://virtualenv.pypa.io/en/latest/)
is highly recommended in order to avoid interfering with other software installed in the system
in which **StegTest** is run.

These are the minimum commands needed to create a virtualenv using python3.6 for **StegTest**:

```bash
pip install virtualenv
virtualenv -p $(which python3.6) stegtest-venv
```

Afterwards, you have to execute this command to activate the virtualenv:

```bash
source stegtest-venv/bin/activate
```

Remember to execute it every time you start a new console to work on **StegTest**!

<!-- Uncomment this section after releasing the package to PyPI for installation instructions
## Install from PyPI

After creating the virtualenv and activating it, we recommend using
[pip](https://pip.pypa.io/en/stable/) in order to install **StegTest**:

```bash
pip install stegtest
```

This will pull and install the latest stable release from [PyPI](https://pypi.org/).
-->

## Install from source

With your virtualenv activated, you can clone the repository and install it from
source by running `make install` on the `stable` branch:

```bash
git clone git@github.com:DAI-Lab/stegtest.git
cd stegtest
make install
```

## Install for Development

If you want to contribute to the project, a few more steps are required to make the project ready
for development.

Please head to the [Contributing Guide](https://DAI-Lab.github.io/stegtest/contributing.html#get-started)
for more details about this process.

# Quickstart

In this short tutorial we will guide you through a series of steps that will help you
getting started with **StegTest**.

Please proceed to [TUTORIAL](notebooks/Tutorial.ipynb) to get started with StegTest

# CLI

StegTest also supports a command line interface. To get started, please have stegtest installed in your system and then type in 
```
stegtest --help
```

This will give you a list of the commands. For each command you can type the command followed by --help to retrieve information specific to that command. 

# Configuration Files

Configuration files provide StegTest with an easy-to-use set of descriptors that define how your steganographic processes operate. Please take a look at some of the example configuration files in the examples/ folder. Each .ini configuration will be labeled by the steganographic procedure's name. This configuration must then follow a restricted specification which only allows for two algorithm types ('detector' | 'embeddor'). 

Each algorithm type will have it's own specific set of specifications as documented in the online manual here ![CONFIGURATION.MD](CONFIGURATION.md).

# What's next?

For more details about **StegTest** and all its possibilities
and features, please check the [documentation site](
https://DAI-Lab.github.io/stegtest/).
