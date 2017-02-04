# trello-google-audit

A small scripts to auditing list of members on Google Sheets, Trello organization and Trello boards of organization.

## Requirements

Application require Python 2.7 and some Python libraries.

## Installation

Install python 2.7: ``sudo apt-get install python2.7 python2.7-dev python-pip``

Install python dependencies: ``pip install -r requirements.txt``

## Usage

    usage: trello-google-audit.py [-h] --key KEY [--sheet SHEET]
                                  [--organization ORGANIZATION] [--csv CSV]

    optional arguments:
      -h, --help            show this help message and exit
      --key KEY             A Google sheet key of published document
      --sheet SHEET         A Google sheet no. of published document (default: 1)
      --organization ORGANIZATION
                            Trello organization name (default: koonaukowegenbit)
      --csv CSV

## Example

Generate tabular report user membership to boards, organization and sheet

``
$ python trello-google-audit.py --key '1-RfXe7NNukxxxxn-xxxxx_Zop-KfNZKaXeFPsg' --csv 'report.csv'; 
``
In effects CSV file with files with content like:

| name                          | plotron | miklaj | ka54mil | tdarkness |
|-------------------------------|---------|--------|---------|-----------|
| NN - ogólna                   | True    | True   | True    | True      |
| google                        | True    | True   | True    | True      |
| trello                        | True    | True   | True    | True      |
| U2F-Token                     | False   | True   | False   | False     |
| Seminaria naukowe i warsztaty | True    | True   | False   | False     |

Generate text report for missing membership to boards, organization and sheet:

``
$  python trello-google-audit.py --key '1-RfXexxxxxx-wTKSehCNi_Zop-KfNZKaXeFPsg'
Google: plotron, tdarkness, mkczyk, miklaj
Extra members of board NN - ogólna to organization: (None)
Extra members of board Seminaria naukowe i warsztaty to organization: (None)
Extra members of board U2F-Token to organization: (None)
Extra members of Google to Trello organization: patkamil
Extra members of Trello organization to Google: (None)

``
