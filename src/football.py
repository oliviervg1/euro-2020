import requests


class FootballClient(object):

    def __init__(self, api_key, competition):
        self.base_endpoint = 'https://api.football-data.org/v2/competitions'
        self.competition = competition
        self.requests = requests.Session()
        self.requests.headers.update({'X-Auth-Token': api_key})
        self._all_teams = None
        self._all_matches = None

    def get_all_teams(self):
        if self._all_teams is None:
            response = self.requests.get(
                '{0}/{1}/teams'.format(
                    self.base_endpoint, self.competition
                )
            )
            response.raise_for_status()
            data = response.json()
            self._all_teams = [
                (team['name'], team['crestUrl']) for team in data['teams']
            ]
        return self._all_teams

    def get_all_matches(self):
        if self._all_matches is None:
            response = self.requests.get(
                '{0}/{1}/matches'.format(
                    self.base_endpoint, self.competition
                )
            )
            response.raise_for_status()
            self._all_matches = response.json()['matches']
        return self._all_matches

    def get_results(self):
        response = self.requests.get(
            '{0}/{1}/matches'.format(
                self.base_endpoint, self.competition
            )
        )
        response.raise_for_status()
        results = {}
        for fixture in response.json()['matches']:
            if (
                fixture['result']['goalsHomeTeam'] is not None and
                fixture['result']['goalsAwayTeam'] is not None
            ):
                game = '{}_{}_{}'.format(
                    fixture['matchday'],
                    fixture['homeTeamName'],
                    fixture['awayTeamName']
                )
                if fixture['result'].get('extraTime'):
                    score = {
                        'home_score': fixture['result']['extraTime']['goalsHomeTeam'],  # noqa
                        'away_score': fixture['result']['extraTime']['goalsAwayTeam']  # noqa
                    }
                else:
                    score = {
                        'home_score': fixture['result']['goalsHomeTeam'],
                        'away_score': fixture['result']['goalsAwayTeam']
                    }
                results[game] = score
        return results

    def check_predictions_validity(self, predictions):
        matches = self.get_all_matches()

        def find_fixture(matchday, home_team, away_team):
            games = [
                fixture for fixture in matches
                if fixture['matchday'] == matchday and
                fixture['homeTeamName'] == home_team and
                fixture['awayTeamName'] == away_team
            ]
            if len(games) != 1:
                raise Exception(
                    'Looks like you tried to predict the score for a game '
                    'that doesn\'t exist.'
                )
            return games[0]

        for prediction in predictions:
            fixture = find_fixture(
                prediction['matchday'],
                prediction['home_team'],
                prediction['away_team']
            )
            if fixture['status'] not in ['SCHEDULED', 'TIMED']:
                raise Exception(
                    'You can\'t set a prediction for a game that isn\'t in a '
                    'scheduled state.'
                )

        return True
