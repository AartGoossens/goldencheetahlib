class GoldenCheetahNotAvailable(Exception):
    def __init__(self, host):
        Exception.__init__(self, 'GC not running at \'{}\''.format(host))


class AthleteDoesNotExist(Exception):
    def __init__(self, athlete):
        Exception.__init__(self, 'Athlete \'{}\' does not exist.'.format(athlete))


class ActivityDoesNotExist(Exception):
    def __init__(self, filename):
        Exception.__init__(self, 'Activity \'{}\' does not exist.'.format(filename))
