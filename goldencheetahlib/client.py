import re
from functools import lru_cache
from io import StringIO
from urllib.parse import quote_plus

import numpy as np
import pandas as pd
import requests

from .constants import (ACTIVITY_COLUMN_ORDER, ACTIVITY_COLUMN_TRANSLATION,
                        DEFAULT_HOST)
from .exceptions import (ActivityDoesNotExist, AthleteDoesNotExist,
                         GoldenCheetahNotAvailable)


class GoldenCheetahClient:
    """Class that provides access to GoldenCheetah's REST API
    Can be used to retrieve lists of and single activities, including raw data.
    """
    def __init__(self, athlete=None, host=DEFAULT_HOST):
        """Initialize GC client.

        Keyword arguments:
        athlete -- Full name of athlete
        host -- the full host (including \'http://\')
        """
        if athlete is not None:
            self.athlete = athlete
        self.host = host

    def get_athletes(self):
        """Get all available athletes
        This method is cached to prevent unnecessary calls to GC.
        """
        response = self._get_request(self.host)
        response_buffer = StringIO(response.text)
        
        return pd.read_csv(response_buffer)

    def get_activity_list(self):
        """Get activity list for client.athlete"""
        return self._request_activity_list(self.athlete)

    def get_athlete_zones(self):
        """Get athlete zones for client.athlete.
        Not implemented yet.
        """
        pass

    def get_activity_by_filename(self, filename):
        """Get raw activity data for filename for self.athlete
        This call is slow and therefore this method is memory cached.

        Keyword arguments:
        filename -- filename of request activity (e.g. \'2015_04_29_09_03_16.json\')
        """
        return self._request_activity_data(self.athlete, filename)

    def get_activity_bulk(self, activities):
        """Get raw activity data in bulk for several activities

        Keyword arguments:
        activities -- (slice of) activity list DataFrame
        """
        for index, filename in activities.filename.iteritems():
            activity_data = self.get_activity_by_filename(filename)
            activities.at[index, 'data'] = activity_data
        return activities

    def get_last_activity(self):
        """Get all activity data for the last activity

        Keyword arguments:
        """
        last_activity = self.get_activity_list().iloc[-1]
        last_activity.data = self.get_activity_by_filename(last_activity.filename)
        return last_activity

    def _request_activity_list(self, athlete):
        """Actually do the request for activity list
        This call is slow and therefore this method is memory cached.

        Keyword arguments:
        athlete -- Full name of athlete
        """
        response = self._get_request(self._athlete_endpoint(athlete))
        response_buffer = StringIO(response.text)
        
        activity_list = pd.read_csv(
            filepath_or_buffer=response_buffer,
            parse_dates={'datetime': ['date', 'time']},
            sep=',\s*',
            engine='python'
        )
        activity_list.rename(columns=lambda x: x.lower(), inplace=True)
        activity_list.rename(
            columns=lambda x: '_' + x if x[0].isdigit() else x, inplace=True)

        activity_list['has_hr'] = activity_list.average_heart_rate.map(bool)
        activity_list['has_spd'] = activity_list.average_speed.map(bool)
        activity_list['has_pwr'] = activity_list.average_power.map(bool)
        activity_list['has_cad'] = activity_list.average_heart_rate.map(bool)
        activity_list['data'] = pd.Series(dtype=np.dtype("object"))
        return activity_list

    def _request_activity_data(self, athlete, filename):
        """Actually do the request for activity filename
        This call is slow and therefore this method is memory cached.

        Keyword arguments:
        athlete -- Full name of athlete
        filename -- filename of request activity (e.g. \'2015_04_29_09_03_16.json\')
        """
        response = self._get_request(self._activity_endpoint(athlete, filename)).json()

        activity = pd.DataFrame(response['RIDE']['SAMPLES'])
        activity = activity.rename(columns=ACTIVITY_COLUMN_TRANSLATION)

        activity.index = pd.to_timedelta(activity.time, unit='s')
        activity.drop('time', axis=1, inplace=True)

        return activity[[i for i in ACTIVITY_COLUMN_ORDER if i in activity.columns]]

    def _athlete_endpoint(self, athlete):
        """Construct athlete endpoint from host and athlete name

        Keyword arguments:
        athlete -- Full athlete name
        """
        return '{host}{athlete}'.format(
            host=self.host,
            athlete=quote_plus(athlete)
        )

    def _activity_endpoint(self, athlete, filename):
        """Construct activity endpoint from host, athlete name and filename

        Keyword arguments:
        athlete -- Full athlete name
        filename -- filename of request activity (e.g. \'2015_04_29_09_03_16.json\')
        """
        return '{host}{athlete}/activity/{filename}'.format(
            host=self.host,
            athlete=quote_plus(athlete),
            filename=filename
        )

    @lru_cache(maxsize=256)
    def _get_request(self, endpoint):
        """Do actual GET request to GC REST API
        Also validates responses.

        Keyword arguments:
        endpoint -- full endpoint for GET request
        """
        try:
            response = requests.get(endpoint)
        except requests.exceptions.RequestException:
            raise GoldenCheetahNotAvailable(endpoint)
        
        if response.text.startswith('unknown athlete'):
            match = re.match(
                pattern='unknown athlete (?P<athlete>.+)',
                string=response.text)
            raise AthleteDoesNotExist(
                athlete=match.groupdict()['athlete'])

        elif response.text == 'file not found':
            match = re.match(
                pattern='.+/activity/(?P<filename>.+)',
                string=endpoint)
            raise ActivityDoesNotExist(
                filename=match.groupdict()['filename'])

        return response
