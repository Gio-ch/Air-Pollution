import os
# import dotenv
# dotenv.load_dotenv()
TBILISI_BOUNDS = [41.6203945, 41.8434205, 44.5967238, 45.0180102]
TOKEN = os.environ.get('TOKEN')
URL = f'https://api.waqi.info/v2/map/bounds?latlng=41.6203945,41.8434205,44.5967238,45.0180102&networks=all&token={TOKEN}'