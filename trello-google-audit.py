#!/bin/python2.7
# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import os

from repoze.lru import lru_cache
from trello import TrelloApi

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


def get_session():
    if 'CACHE_REQUESTS' in os.environ:
        import requests_cache
        return requests_cache.CachedSession()
    import requests
    return requests.Session()


def trello_init():
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
    return trello


def google_fetch(key, sheet=1):
    url = "https://spreadsheets.google.com/feeds/list/%s/%d/public/values?alt=json" % (
        key, sheet)
    return get_session().get(url).json()


def build_args():
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
                        default='koonaukowegenbit')
    return parser.parse_args()


@lru_cache(maxsize=64)
def get_member_name(trello, idMember):
    return trello.members.get(idMember)['username']


def get_google_members(google):
    return {x['gsx$trello']['$t'] for x in google['feed']['entry'] if x['gsx$trello']['$t']}


def get_organization_members(trello, name):
    return {x['username'] for x in trello.organizations.get_member(name)}


def get_board_member(trello, board):
    return {get_member_name(trello, member['idMember']) for member in board['memberships']}


def print_extra_boards_members(trello, org_members, organization):
    for board in trello.organizations.get_board('koonaukowegenbit'):
        members = get_board_member(trello, board)
        extra_members = members - org_members
        print("Extra members of board {board} to organization:".format(board=board['name']),
              ", ".join(extra_members) or '(None)')


def print_extra_members(org_m, google_m):
    print("Extra members of Google to Trello organization:",
          ", ".join(org_m - google_m) or '(None)')
    print("Extra members of Trello organization to Google:",
          ", ".join(google_m - org_m) or '(None)')


def main():
    args = build_args()
    trello = trello_init()
    google = google_fetch(args.key, args.sheet)
    organization_members = get_organization_members(trello, args.organization)
    google_members = get_google_members(google)

    print_extra_boards_members(trello, organization_members, args.organization)
    print_extra_members(organization_members, google_members)


if __name__ == '__main__':
    main()
