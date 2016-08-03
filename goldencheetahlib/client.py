from functools import lru_cache
from urllib.parse import quote_plus

import pandas as pd
import requests


DEFAULT_HOST = 'http://localhost:12021/'


class GCClient:
    def __init__(self, athlete=None, host=DEFAULT_HOST):
        self.athlete = athlete
        self.host = host

    def get_athletes(self):
        return pd.read_csv(self.host)

    def get_activity_list(self):
        activity_list = pd.read_csv(
            filepath_or_buffer=self.athlete_endpoint(),
            parse_dates={'datetime': ['date', ' time']}
        )

        activity_list.rename(columns=lambda x: x.lstrip().lower(), inplace=True)
        activity_list.rename(
            columns=lambda x: '_' + x if x[0].isdigit() else x, inplace=True)

        activity_list['has_hr'] = activity_list.average_heart_rate.map(bool)
        activity_list['has_spd'] = activity_list.average_speed.map(bool)
        activity_list['has_pwr'] = activity_list.average_power.map(bool)
        activity_list['has_cad'] = activity_list.average_heart_rate.map(bool)

        return activity_list

    def get_athlete_zones(self):
        pass

    @lru_cache(maxsize=256)
    def get_activity_by_filename(self, activity_id):
        if not self.athlete:
            raise Exception('self.athlete not defined')

        resp = requests.get(self.activity_endpoint(activity_id))
        activity = pd.DataFrame(resp.json()['RIDE']['SAMPLES'])
        return activity

    def get_activity(self, activity):
        filename = activity['filename']
        return self.get_activity_by_filename(filename)
    
    def get_activity_bulk(self, activities):
        retrieved_activities = []
        for act in activities.iterrows():
            retrieved_activities.append(self.get_activity(act[1]))
        return retrieved_activities

    def get_last_activity(self):
        activity_list = self.get_activity_list()
        return self.get_activity(activity_list.iloc[-1])

    def encoded_athlete(self):
        return quote_plus(self.athlete)

    def athlete_endpoint(self):
        return '{host}{athlete}'.format(
            host=self.host,
            athlete=self.encoded_athlete()
        )

    def activity_endpoint(self, filename):
        return '{host}{athlete}/activity/{filename}'.format(
            host=self.host,
            athlete=self.encoded_athlete(),
            filename=filename
        )
