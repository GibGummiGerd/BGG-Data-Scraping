# BGG-Data

- [BGG-Data](#bgg-data)
  - [What is BGG-Data](#what-is-bgg-data)
  - [Installation](#installation)
    - [Python 3](#python-3)
      - [Linux](#linux)
      - [Windows](#windows)
    - [Pip](#pip)
      - [Linux](#linux-1)
      - [Windows](#windows-1)
    - [Pipenv](#pipenv)
    - [Start Virtual environment and install packages](#start-virtual-environment-and-install-packages)
    - [Start Scraper](#start-scraper)

## What is BGG-Data

This is a program to scrape data from BoardGameGeek (BGG)

## Installation

### Python 3

#### Linux

Python should be installed with your Linux distribution.

``` bash
python3 --version
```

#### Windows

``` bash
python --version
```

### Pip

#### Linux

``` bash
sudo apt install python3-pip
```

#### Windows

Pip should be installed with your Python installation. You can check if pip is insatlled with

``` bash
pip --version
```

### Pipenv

``` bash
sudo pip install pipenv
```

### Start Virtual environment and install packages

``` bash
cd bgg-data
pipenv shell
pipenv install
```

### Start Scraper

``` bash
cd scraper
W: python main.py
L: python3 main.py
```