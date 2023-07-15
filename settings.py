import os
TBILISI_BOUNDS = [41.6203945, 41.8434205, 44.5967238, 45.0180102]
TOKEN = os.environ.get('TOKEN')
URL = f'https://api.waqi.info/v2/map/bounds?latlng=41.6203945,41.8434205,44.5967238,45.0180102&networks=all&token={TOKEN}'
DATASET_ID = os.environ.get('DATASET_ID')
TABLE_ID = os.environ.get('TABLE_ID')
PROJECT_ID = os.environ.get('PROJECT_ID')
