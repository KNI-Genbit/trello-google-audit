# trello-google-audit

A small scripts to auditing list of members on Google Sheets, Trello organization and Trello boards of organization.

## Requirements

Application require Python 2.7 and some Python libraries.

## Installation

Install python 2.7: ``sudo apt-get install python2.7 python2.7-dev python-pip``

Install python dependencies: ``pip install -r requirements.txt``

## Usage

    usage: trello-google-audit.py [-h] --key KEY [--sheet SHEET]
                                  [--organization ORGANIZATION]

    optional arguments:
      -h, --help            show this help message and exit
      --key KEY             A Google sheet key of published document
      --sheet SHEET         A Google sheet no. of published document (default: 1)
      --organization ORGANIZATION
                            Trello organization name (default: koonaukowegenbit)
