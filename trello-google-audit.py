#!/bin/python2.7
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import argparse
import logging

import requests
from cached_property import cached_property
from repoze.lru import lru_cache
from trello import TrelloApi
from unicodecsv import DictWriter

try:
    TRELLO_APP_KEY = open('.app_key.txt').read().strip()
except IOError:
    TRELLO_APP_KEY = raw_input("Please enter Trello app key (see https://trello.com/app-key): ")
    open('.app_key.txt', 'wb').write(TRELLO_APP_KEY)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

GOOGLE_KEY_FILE = '.key.txt'
GOOGLE_SHEET_FILE = '.sheet.txt'


class TrelloOrganization(object):
    def __init__(self, api, organization):
        self.api = api
        self.organization = organization

    @classmethod
    def init(cls, organization):
        trello = TrelloApi(TRELLO_APP_KEY)
        try:
            trello.set_token(open('.token.txt').read().strip())
            logger.debug("Trello token loaded")
        except IOError:
            token_url = trello.get_token_url('Trello ', expires='never', write_access=True)
            print("Enter following URL in your browser:", token_url)
            token = raw_input("Enter token please:")
            open('.token.txt', 'w').write(token)
            trello.set_token(token)
        return cls(trello, organization)

    @cached_property
    def organization_members(self):
        return {x['username'] for x in self.api.organizations.get_member(self.organization)}

    def _get_board_member(self, board):
        return {self.get_member_name(member['idMember']) for member in board['memberships']}

    @cached_property
    def boards(self):
        return self.api.organizations.get_board(self.organization)

    @lru_cache(maxsize=64)
    def get_member_name(self, idMember):
        return self.api.members.get(idMember)['username']

    @cached_property
    def board_members(self):
        return {board['name']: self._get_board_member(board) for board in self.boards}


class Google(object):
    def __init__(self, key, sheet):
        self.key = key
        self.sheet = sheet
        self.session = requests.Session()
        self.content = self._fetch()

    @cached_property
    def members(self):
        return {x['gsx$trello']['$t']
                for x in self.content['feed']['entry']
                if x['gsx$trello']['$t']}

    def _fetch(self):
        url = "https://spreadsheets.google.com/feeds/list/%s/%d/public/values?alt=json" % (
            self.key, self.sheet)
        response = self.session.get(url)
        return response.json()


class Auditor(object):

    def __init__(self, trello, google):
        self.google = google
        self.trello = trello

    def extra_boards_members(self):
        return {board: (members - self.trello.organization_members)
                for board, members in self.trello.board_members.items()}.items()

    def extra_organization_members(self):
        org_m = self.trello.organization_members
        google_m = self.google.members
        return (org_m - google_m), (google_m - org_m)

    def get_members(self):
        trello_members = self.trello.organization_members
        google_members = self.google.members
        board_members = self.trello.board_members
        return trello_members, google_members, board_members


class CLI(object):
    def __init__(self, auditor):
        self.auditor = auditor

    def get_members(self):
        print("Google:", ", ".join(self.auditor.google.members))

    def print_extra_boards_members(self):
        for board, extra_members in self.auditor.extra_boards_members():
            print("Extra members of board {board} to organization:".format(board=board),
                  ", ".join(extra_members) or '(None)')

    def print_extra_members(self):
        to_trello, to_google = self.auditor.extra_organization_members()

        print("Extra members of Google to Trello organization:",
              ", ".join(to_trello) or '(None)')
        print("Extra members of Trello organization to Google:",
              ", ".join(to_google) or '(None)')

    def report(self):
        self.get_members()
        self.print_extra_boards_members()
        self.print_extra_members()


class CSV(object):
    def __init__(self, auditor, filename='report.csv'):
        self.auditor = auditor
        self.filename = filename

    def report(self):
        trello_members, google_members, board_members = self.auditor.get_members()
        all_members = set()
        all_members.update(trello_members)
        all_members.update(google_members)
        for members in board_members.values():
            all_members.update(members)

        with open(self.filename, 'wb+') as fp:
            csv = DictWriter(fp, ['name'] + list(all_members))
            csv.writeheader()
            board_members['google'] = google_members
            board_members['trello'] = trello_members

            for board, members in board_members.items():
                row = {member: (member in members) for member in all_members}
                row['name'] = board
                csv.writerow(row)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--key",
                        help="A Google sheet key of published document",
                        required=True)
    parser.add_argument("--sheet",
                        help="A Google sheet no. of published document (default: 1)",
                        required=False,
                        default=1,
                        type=int)
    parser.add_argument("--organization",
                        help="Trello organization name (default: koonaukowegenbit)",
                        default='uphnn')
    parser.add_argument("--csv", type=str, default=None)

    args = parser.parse_args()
    auditor = Auditor(trello=TrelloOrganization.init(args.organization),
                      google=Google(args.key, args.sheet))
    if args.csv:
        CSV(auditor, args.csv).report()
    else:
        CLI(auditor).report()


if __name__ == '__main__':
    main()
