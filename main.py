#!/usr/bin/env python3
"""
CFB Model
"""

__author__ = "Drew Blocki"
__version__ = "0.1.0"
__license__ = "MIT"

from enum import Enum
from logzero import logger
import os
from statistics import mean

import cfbd
from cfbd.rest import ApiException
import pandas

apiKey = os.getenv('CFBD_API_KEY')

class PlayType(Enum):
    RUSH = 'rush'
    PASS = 'pass'

"""
Calculates percentage of yards/play allowed by a team from Week 1 to the specified week 
compared to opponent average
"""
def getTeamPercentageAllowed(year: int, week: int, team: str, type: PlayType, apiClient) -> float:
    gamesApi = cfbd.GamesApi(apiClient)
    statsApi = cfbd.StatsApi(apiClient)

    # iterate over team's games from week 2-{week param}
    games = gamesApi.get_games(year, team=team)
    for game in games:
        logger.info(game)
    #       calculate A = opponents yards per play for that game
    #       calculate B = opponents yards per play outside of that game
    #       push C = A / B into a list
    # return average of list
    return 0

def main():
    """ Main entry point of the app """
    logger.debug('Run the Damn Ball!\n')

    configuration = cfbd.Configuration()
    logger.debug(f'apiKey: {apiKey}')
    configuration.api_key['Authorization'] = apiKey
    configuration.api_key_prefix['Authorization'] = 'Bearer'
    apiClient = cfbd.ApiClient(configuration)

    teams = ['Penn State', 'Ohio State']
    week = 8
    year = 2017

    for team in teams:
        rushDefensePct = getTeamPercentageAllowed(year, week, team, PlayType.RUSH, apiClient)
        passDefensePct = getTeamPercentageAllowed(year, week, team, PlayType.PASS, apiClient)
        logger.info(f'{team}')
        logger.info(f'\tRush Defense %: {rushDefensePct}')
        logger.info(f'\tPass Defense %: {passDefensePct}\n')

if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()
