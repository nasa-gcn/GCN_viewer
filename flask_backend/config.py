import os

def alchemy_uri():
	return 'sqlite:///database/circulars.db'

def bind_uri():
	return {'db1': alchemy_uri(),
    'db2': 'sqlite:///database/events.db',
    'db3': 'sqlite:///database/observatories.db',
    'db4': 'sqlite:///database/missions.db',
    'db5': 'sqlite:///database/notices.db',
    'db6': 'sqlite:///database/details.db',
    'db7': 'sqlite:///database/eventNotices.db',
    'db8': 'sqlite:///database/mmmw.db',
    'db9': 'sqlite:///database/circular_body.db',}
