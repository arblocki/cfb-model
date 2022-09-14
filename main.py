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
configuration = cfbd.Configuration()
configuration.api_key['Authorization'] = apiKey
configuration.api_key_prefix['Authorization'] = 'Bearer'

apiClient = cfbd.ApiClient(configuration)
gamesApi = cfbd.GamesApi(apiClient)
statsApi = cfbd.StatsApi(apiClient)

class PlayType(Enum):
    RUSH = 'rush'
    PASS = 'pass'
    All = 'all'

FIELD_NAMES = {
    PlayType.RUSH: {
        'yards': 'rushingYards',
        'plays': 'rushingAttempts',
        'yardsPerPlay': 'yardsPerRushAttempt',
    },
    PlayType.PASS: {
        'yards': 'netPassingYards',
        'plays': 'completionAttempts',  # Formatted as {completed passes}-{attempts} so some extra RegEx needed
        'yardsPerPlay': 'yardsPerPass',
    },
}


def getYardsPerPlayByGame(team: str, gameId: int, year: int, type: PlayType) -> float:
    try:
        gameStats = gamesApi.get_team_game_stats(year, game_id=gameId)
    except ApiException as e:
        logger.exception(e)
        return 0
    logger.warning(gameStats)
    
    if team == gameStats[0].teams[0]['school']:
        teamStatsList = gameStats[0].teams[0]['stats']
    else:
        teamStatsList = gameStats[0].teams[1]['stats']
    statMap = {statObj['category']: statObj['stat'] for statObj in teamStatsList}
    logger.warning(statMap)

    return 60
    


def getYardsPerPlayBaseline(opponent: str, gameWeek: int, type: PlayType) -> float:
    return 100


"""
Calculates percentage of yards/play allowed by a team from Week 1 to the specified week 
compared to opponent average
"""
def getTeamPercentageAllowed(year: int, week: int, team: str, type: PlayType) -> float:
    try:
        fullGameList = gamesApi.get_games(year, team=team)
    except ApiException as e:
        logger.exception(e)
        fullGameList = []

    # iterate over team's games from week 2-{week param}
    games = [g for g in fullGameList if g.week <= week]
    percentageAllowedByWeek = []
    for game in games:
        awayTeam = game.away_team
        homeTeam = game.home_team
        gameWeek = game.week

        if team == awayTeam:
            opponent = homeTeam
        else:
            opponent = awayTeam

        logger.debug(f'Analyzing Week {gameWeek} between {awayTeam}-{homeTeam}')

        # Calculate opponent's yards per play against {team}
        oppYardsPerPlay = getYardsPerPlayByGame(opponent, game.id, year, type)
        logger.debug(f'\t{opponent} {type.value} yds per play: {oppYardsPerPlay}')

        # Calculate opponent's yards per play outside of (or prior to?) the game against {team}
        oppYardsPerPlayBaseline = getYardsPerPlayBaseline(opponent, gameWeek, type)
        logger.debug(f'\t{opponent} {type.value} yds per play baseline: {oppYardsPerPlayBaseline}')

        percentageAllowed = oppYardsPerPlay / oppYardsPerPlayBaseline * 100
        logger.debug(f'\t{type.value} Percentage allowed vs {opponent}: {percentageAllowed}%')
        percentageAllowedByWeek.append(percentageAllowed)

    logger.debug(percentageAllowedByWeek)
    meanPctAllowed = mean(percentageAllowedByWeek)

    return meanPctAllowed


def main():
    """ Main entry point of the app """
    logger.debug('Run the Damn Ball!\n')

    teams = ['Ohio State']
    week = 2
    year = 2017

    for team in teams:
        rushDefensePct = getTeamPercentageAllowed(year, week, team, PlayType.RUSH)
        passDefensePct = getTeamPercentageAllowed(year, week, team, PlayType.PASS)
        logger.info(f'{team}')
        logger.info(f'\tRush Defense %: {rushDefensePct}')
        logger.info(f'\tPass Defense %: {passDefensePct}\n')

if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()
