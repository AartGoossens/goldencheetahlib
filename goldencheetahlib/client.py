from functools import lru_cache
from urllib.parse import quote_plus

import matplotlib
import numpy as np
import pandas as pd
import requests

from .constants import (
    DEFAULT_HOST, ACTIVITY_COLUMN_TRANSLATION, ACTIVITY_COLUMN_ORDER)


class GoldenCheetahClient:
    def __init__(self, athlete=None, host=DEFAULT_HOST):
        self.athlete = athlete
        self.host = host

    @lru_cache()
    def get_athletes(self):
        return pd.read_csv(self.host)

    def get_activity_list(self):
        return self._request_activity_list(self.athlete)

    @lru_cache()
    def _request_activity_list(self, athlete):
        if not self.athlete:
            raise Exception('self.athlete not defined')
        activity_list = pd.read_csv(
            filepath_or_buffer=self._athlete_endpoint(athlete),
            parse_dates={'datetime': ['date', ' time']}
        )
        activity_list.rename(columns=lambda x: x.lstrip().lower(), inplace=True)
        activity_list.rename(
            columns=lambda x: '_' + x if x[0].isdigit() else x, inplace=True)

        activity_list['has_hr'] = activity_list.average_heart_rate.map(bool)
        activity_list['has_spd'] = activity_list.average_speed.map(bool)
        activity_list['has_pwr'] = activity_list.average_power.map(bool)
        activity_list['has_cad'] = activity_list.average_heart_rate.map(bool)
        activity_list['data'] = pd.Series(dtype=np.dtype("object"))
        return activity_list

    def get_athlete_zones(self):
        pass

    @lru_cache(maxsize=256)
    def _request_activity_data(self, athlete, filename):
        if not self.athlete:
            raise Exception('self.athlete not defined')
        response = requests.get(self._activity_endpoint(athlete, filename)).json()

        activity = pd.DataFrame(response['RIDE']['SAMPLES'])
        activity.rename(columns=ACTIVITY_COLUMN_TRANSLATION, inplace=True)

        activity.index = pd.to_timedelta(activity.time, unit='s')
        activity.drop('time', axis=1, inplace=True)

        return activity[[i for i in ACTIVITY_COLUMN_ORDER if i in activity.columns]]
    
    def get_activity_by_filename(self, filename):
        return self._request_activity_data(self.athlete, filename)

    def get_activity_bulk(self, activities):
        for index, filename in activities.filename.iteritems():
            activity_data = self.get_activity_by_filename(filename)
            activities.set_value(index, 'data', activity_data)
        return activities

    def get_last_activity(self):
        last_activity = self.get_activity_list().iloc[-1]
        last_activity.set_value('data', self.get_activity_by_filename(last_activity.filename))
        return last_activity

    def _athlete_endpoint(self, athlete):
        return '{host}{athlete}'.format(
            host=self.host,
            athlete=quote_plus(athlete)
        )

    def _activity_endpoint(self, athlete, filename):
        return '{host}{athlete}/activity/{filename}'.format(
            host=self.host,
            athlete=quote_plus(athlete),
            filename=filename
        )
