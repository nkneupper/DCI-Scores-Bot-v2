#!/usr/bin/env python3

import json
from typing import List, Dict, Tuple, Union

import praw
import requests

from config import username, password, client_id, client_secret, show_file

BOT_INFO = (
    "*I'm a bot! Check me out on " +
    "[GitHub](https://github.com/bradysalz/DCI-Scores-Bot-v2)!" +
    " Please PM me with any additional feedback.* \n\n" + "*Hope you enjoy!*")

ORG_URL = "https://api.competitionsuite.com/2018-03/competitions"
COMP_URL = "https://api.competitionsuite.com/2018-03/performances"
DCI_API_ID = '96b77ec2-333e-41e9-8d7d-806a8cbe116b'
YEAR = '2022'


class WebBot(object):
    """Bot that interacts with the big world wide web.

    In reality, only goes on two sites:
        - dci.org, for parsing and checking for show updates
        - reddit.com, for posting said updates

    Primary functionality is parsing JSON information and formatting that to
    a markdown-based reddit post.
    """

    def __init__(self, subreddit: str='dcicsstest'):
        self.show_file = show_file
        self.subreddit = subreddit
        self.__agent__ = 'python:dci-scores-tracker:2.0 (by /u/dynerthebard)'
        self.conn = None

    def connect(self):
        """Connects to Google Sheets"""
        # Placeholder. Will write to google sheets after initial data extraction complete
        print('Connected to Google Sheets')

    def _find_bluecoats(self, show_scores: List[Dict]) -> Union[Dict, bool]:
        """Determines if Bluecoats were in the competition"""
        for corps in show_scores:
            if corps['GroupName'] == 'Bluecoats':
                return corps
        return False

    def _parse_show_recap(self, show_rounds: List[Dict]) -> str:
        """Reads through show query and formats to a reddit post."""
        body_str = ''

        for _round in show_rounds:
            body_str += '## ' + _round['name'] + '\n\n'
            body_str += '[Full Recap Here](' + _round['fullRecapUrl'] + ')\n\n'

            body_str += 'Rank|Corp|Score\n'
            body_str += ':--|:--|:--\n'

            for perf in _round['performances']:
                body_str += '{}|{}|{:.2f}\n'.format(perf['rank'], perf['name'],
                                                    perf['score'])

            body_str += '\n\n---\n\n'

        body_str += '\n\n' + BOT_INFO
        return body_str

    def _parse_visual_caption(self, scores: List[Dict]) -> List[Dict]:
        """Parses score captions and returns a list of tuples

        scores: a list of objects containing the four score captions: GE, Music, Visual, Penalties
        returns: a list of dictionaries containing the judge name, judge subcaption, and score for each visual subcaption
        {
            fullName: string
            subcaption: string
            content: string
            achievement: string
        }
        """
        body = []
        for caption in scores:
            if caption['Name'] == 'Visual':
                for subcaption in caption['Captions']:
                    data = {
                        'fullName': None,
                        'subcaption': None,
                        'content': None,
                        'achievement': None,
                    }
                    data['fullName'] = subcaption['JudgeFirstName'] + \
                        ' ' + subcaption['JudgeLastName']
                    data["subcaption"] = subcaption["Name"]
                    data['content'] = subcaption["Subcaptions"][0]['Score']
                    data['achievement'] = subcaption['Subcaptions'][1]['Score']
                    body.append(data)

        return body

    def _parse_show_info(self, show_info: Dict) -> Tuple[str, Union[str, None]]:
        """Pings show's GUID and returns the title and recap post.

        show_guid: an API GUID that corresponds to a certain show
        returns: a two-item tuple with the formatted title and reddit body
        """
        show_guid = show_info["CompetitionGuid"]
        api_keys = {'c': show_guid}
        resp = requests.get(COMP_URL, params=api_keys)

        content = resp.content.decode('utf-8')
        show = json.loads(content)

        # This is where to parse the show details.
        # show object above is a list
        # for each object in list, determine if Bluecoats are a competitor
        # If so, then parse down to the visual subcaptions
        # This can associate scores by judge
        bluecoats = self._find_bluecoats(show)
        if bluecoats:
            title_str = show_info['EventName']
            body = self._parse_visual_caption(bluecoats['Categories'])
            return (title_str, body)
        return ('', None)

    def post_rows(self, show_info: Dict):
        """Updates Google Spreadsheet

        show_info: a Dict of all the JSON response info on the show
        """
        title, body = self._parse_show_info(show_info)
        if body:
            print(title)
            print(body)

    def get_show_list(self) -> List[Dict]:
        """Scrapes the DCIs.org API site and returns a list of shows"""
        api_keys = {'year': YEAR}

        resp = requests.get(ORG_URL, params=api_keys)

        content = resp.content.decode('utf-8')

        # Strip off jquery tags from the response string
        return json.loads(content)
