from unittest import TestCase, skip

import numpy as np
import pandas as pd

from goldencheetahlib import GoldenCheetahClient, exceptions
from tests.vcr_config import vcr


class TestGoldenCheetahClient(TestCase):
    def setUp(self):
        self.client = GoldenCheetahClient(athlete='Aart')

    def test_client_init(self):
        client = GoldenCheetahClient(athlete='Aart')
        self.assertTrue(client)
        self.assertTrue(client.athlete)
        self.assertTrue(client.host)

    def test_client_init_without_athlete(self):
        client = GoldenCheetahClient()
        self.assertFalse(hasattr(client, 'athlete'))
        self.assertTrue(client.host)

    def test_client_init_non_existing_athlete(self):
        client = GoldenCheetahClient(athlete='NonExistingAthlete')
        self.assertTrue(client)
        self.assertTrue(client.athlete)
        self.assertTrue(client.host)

    def test_get_athletes(self):
        with vcr.use_cassette('test_get_athletes.yaml') as cass:
            athletes = self.client.get_athletes()
            self.assertEqual(
                'http://localhost:12021/',
                cass.requests[0].uri)

            self.assertTrue(isinstance(athletes, pd.DataFrame))
            self.assertEqual(2, len(athletes))
            self.assertTrue('name' in athletes.columns)
            self.assertTrue('dob' in athletes.columns)
            self.assertTrue('weight' in athletes.columns)
            self.assertTrue('height' in athletes.columns)
            self.assertTrue('sex' in athletes.columns)

    def test_get_athletes_invalid_host(self):
        self.client.host = 'http://localhost:123456/'
        with self.assertRaises(exceptions.GoldenCheetahNotAvailable):
            self.client.get_athletes()

    def test_get_athletes_invalid_host_non_http(self):
        self.client.host = 'blalocalhost:123456/'
        with self.assertRaises(exceptions.GoldenCheetahNotAvailable):
            self.client.get_athletes()

    def test_get_activity_list(self):
        with vcr.use_cassette('test_get_activity_list.yaml') as cass:
            activity_list = self.client.get_activity_list()
            self.assertEqual(
                'http://localhost:12021/Aart',
                cass.requests[0].uri)

            self.assertTrue(isinstance(activity_list, pd.DataFrame))
            self.assertEqual(235, len(activity_list))
            self.assertTrue('data' in activity_list.columns)
            self.assertTrue(isinstance(activity_list.data[0], np.float))
            self.assertTrue('datetime' in activity_list.columns)
            self.assertTrue('axpower' in activity_list.columns)
            self.assertFalse(' filename' in activity_list.columns)

    def test_get_activity_list_incorrect_host(self):
        self.client.host = 'http://localhost:123456/'
        with self.assertRaises(exceptions.GoldenCheetahNotAvailable):
            self.client.get_activity_list()

    def test_get_activity_list_non_existing_athlete(self):
        with vcr.use_cassette('test_get_activity_list_non_existing_athlete.yaml') as cass:
            self.client.athlete = 'John Non Existent'
            with self.assertRaises(exceptions.AthleteDoesNotExist):
                self.client.get_activity_list()

    def test_get_activity_by_filename(self):
        with vcr.use_cassette('test_get_activity_by_filename.yaml') as cass:
            filename = '2014_01_06_16_45_24.json'
            activity = self.client.get_activity_by_filename(filename)
            self.assertEqual(
                'http://localhost:12021/Aart/activity/{}'.format(filename),
                cass.requests[0].uri)

            self.assertTrue(isinstance(activity, pd.DataFrame))
            self.assertEqual(6722, len(activity))
            self.assertEqual(6, len(activity.columns))
            self.assertTrue('speed' in activity.columns)
            self.assertTrue('distance' in activity.columns)
            self.assertTrue('altitude' in activity.columns)
            self.assertTrue('slope' in activity.columns)
            self.assertTrue('latitude' in activity.columns)
            self.assertTrue('longitude' in activity.columns)

    def test_get_activity_by_filename_incorrect_host(self):
        self.client.host = 'http://localhost:123456/'
        with self.assertRaises(exceptions.GoldenCheetahNotAvailable):
            filename = '2014_01_06_16_45_24.json'
            self.client.get_activity_by_filename(filename)

    def test_get_activity_by_filename_non_existing_athlete(self):
        with vcr.use_cassette('test_get_activity_by_filename_non_existing_athlete.yaml') as cass:
            self.client.athlete = 'John Non Existent'
            filename = '2014_01_06_16_45_24.json'
            with self.assertRaises(exceptions.AthleteDoesNotExist):
                self.client.get_activity_by_filename(filename)

    def test_get_activity_by_non_existing_filename(self):
        with vcr.use_cassette('test_get_activity_by_non_existing_filename.yaml') as cass:
            filename = 'non_existing_filename.json'
            with self.assertRaises(exceptions.ActivityDoesNotExist):
                self.client.get_activity_by_filename(filename)

    def test_get_activity_bulk(self):
        with vcr.use_cassette('test_get_activity_bulk.yaml') as cass:
            activity_list = self.client.get_activity_list()
            bulk = self.client.get_activity_bulk(activity_list.iloc[:3])
            self.assertEqual(
                'http://localhost:12021/Aart',
                cass.requests[0].uri)
            self.assertEqual(
                'http://localhost:12021/Aart/activity/{}'.format(bulk.filename[0]),
                cass.requests[1].uri)
            self.assertEqual(
                'http://localhost:12021/Aart/activity/{}'.format(bulk.filename[1]),
                cass.requests[2].uri)
            self.assertEqual(
                'http://localhost:12021/Aart/activity/{}'.format(bulk.filename[2]),
                cass.requests[3].uri)

            self.assertTrue(isinstance(bulk, pd.DataFrame))
            self.assertEqual(3, len(bulk))
            self.assertTrue(isinstance(bulk.data[0], pd.DataFrame))

    def test_get_last_activity(self):
        with vcr.use_cassette('test_get_last_activity.yaml') as cass:
            last_activity = self.client.get_last_activity()
            self.assertEqual(
                'http://localhost:12021/Aart',
                cass.requests[0].uri)
            self.assertEqual(
                'http://localhost:12021/Aart/activity/{}'.format(last_activity.filename),
                cass.requests[1].uri)

            self.assertTrue(isinstance(last_activity, pd.Series))
            self.assertTrue('datetime' in last_activity.keys())
            self.assertTrue('axpower' in last_activity.keys())
            self.assertTrue(isinstance(last_activity['data'], pd.DataFrame))
            self.assertEqual(285, len(last_activity))

    def test__request_activity_list(self):
        with vcr.use_cassette('test__request_activity_list.yaml') as cass:
            activity_list = self.client._request_activity_list(self.client.athlete)
            self.assertEqual(
                'http://localhost:12021/Aart',
                cass.requests[0].uri)

            self.assertTrue(isinstance(activity_list, pd.DataFrame))
            self.assertEqual(235, len(activity_list))
            self.assertTrue('data' in activity_list.columns)
            self.assertTrue(isinstance(activity_list.data[0], np.float))
            self.assertTrue('datetime' in activity_list.columns)
            self.assertTrue('axpower' in activity_list.columns)
    
    def test__request_activity_data(self):
        with vcr.use_cassette('test__request_activity_data.yaml') as cass:
            filename = '2014_01_06_16_45_24.json'
            activity = self.client._request_activity_data(self.client.athlete, filename)
            self.assertEqual(
                'http://localhost:12021/Aart/activity/{}'.format(filename),
                cass.requests[0].uri)

            self.assertTrue(isinstance(activity, pd.DataFrame))
            self.assertEqual(6722, len(activity))
            self.assertEqual(6, len(activity.columns))
            self.assertTrue('speed' in activity.columns)
            self.assertTrue('distance' in activity.columns)
            self.assertTrue('altitude' in activity.columns)
            self.assertTrue('slope' in activity.columns)
            self.assertTrue('latitude' in activity.columns)
            self.assertTrue('longitude' in activity.columns)

    def test__request_activity_list_caching(self):
        with vcr.use_cassette('test__request_activity_list_caching.yaml') as cass:
            self.client._request_activity_list(self.client.athlete)
            self.client._request_activity_list(self.client.athlete)
            self.assertEqual(1, len(cass.requests))

    def test__request_activity_data_caching(self):
        with vcr.use_cassette('test__request_activity_data_caching.yaml') as cass:
            filename = '2014_01_06_16_45_24.json'
            self.client._request_activity_data(self.client.athlete, filename)
            self.client._request_activity_data(self.client.athlete, filename)
            self.assertEqual(1, len(cass.requests))


    def test__athlete_endpoint(self):
        endpoint = self.client._athlete_endpoint(self.client.athlete)
        self.assertEqual(endpoint, 'http://localhost:12021/Aart')

    def test__activity_endpoint(self):
        filename = '2014_01_06_16_45_24.json'
        endpoint = self.client._activity_endpoint(self.client.athlete, filename)
        self.assertEqual(endpoint,
            'http://localhost:12021/Aart/activity/2014_01_06_16_45_24.json')
    
    def test_get_athlete_zones(self):
        zones = self.client.get_athlete_zones()
        self.assertTrue(zones is None)
