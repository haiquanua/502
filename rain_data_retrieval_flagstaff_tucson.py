 import sys
 import argparse
 import json
 import logging
 import numpy as np
 import pandas as pd
 import requests
 
 RAINLOG_API_BASE = 'https://rainlog.org/api/'
 RAINLOG_VERSIONED_API_BASE = RAINLOG_API_BASE + '1.0/'
 RAINLOG_READING_GETFILTERED = \
     RAINLOG_VERSIONED_API_BASE + 'Reading/getFiltered'
 RAINLOG_GAUGE_GETFILTERED = RAINLOG_VERSIONED_API_BASE + 'Gauge/getFiltered'
 RAINLOG_GAUGEREVISION_GETFILTERED = \
     RAINLOG_VERSIONED_API_BASE + 'GaugeRevision/getFiltered'
 RAINLOG_DEFAULT_HEADERS_NO_AUTH = {'content-type': 'application/json'}
 
url='https://rainlog.org/api/'
 
 CIRCLE_NEAR_UA = {
     "type": "Circle",
     "center": {'lat': 32.2133, 'lng': -110.9542},
     "radius": .1  # in miles
 }
 
 BOX_NEAR_UA = {
     "type": "Rectangle",
     "westLng": -111.0488008,
     "eastLng": -110.8488008,
     "northLat": 32.3332841,
     "southLat": 32.1332841,
 }
 
 BOX_TUCSON = {
     "type": "Rectangle",
     "westLng": -111.432962,
     "eastLng": -110.4512513,
     "northLat": 32.599326,
     "southLat": 31.689010,
 }

 BOX_FLAGSTAFF = {
     "type": "Rectangle",
     "westLng": -111.706160,
     "eastLng": -111.504286,
     "northLat": 35.242277,
     "southLat": 35.118246,

 }

 def api_post(url, params):
     logging.info('Posting to %s with %s', url, json)
     r = requests.post(
         url,
         headers=RAINLOG_DEFAULT_HEADERS_NO_AUTH,
         json=params
     )
     r.raise_for_status()
     return r.content
 
 
 def parse_date(datetimelike):
     dt = pd.Timestamp(datetimelike)
     return dt.strftime('%Y-%m-%d')
 
 
 def get_readings(start, end, region, limit=None):
     params = {
         'dateRangeStart': parse_date(start),
         'dateRangeEnd': parse_date(end),
         'region': region,
     }
     if limit:
         params['pagination'] = {'limit': 3}
     readings = api_post(RAINLOG_READING_GETFILTERED, params)
     return readings
 
 
 def readings_to_gauge_revision_ids(readings):
     if isinstance(readings, pd.DataFrame):
         revision_ids = readings['gaugeRevisionId'].unique().tolist()
     else:
         raise TypeError('unsupported readings type')
     return revision_ids
 
 
 def get_gauge_revisions(revision_ids, start, end, region):
     params = {
         'dateRangeStart': parse_date(start),
         'dateRangeEnd': parse_date(end),
         'region': region,
         'gaugeRevisionIds': revision_ids
     }
     revisions = api_post(RAINLOG_GAUGEREVISION_GETFILTERED, params)
     return revisions
 
 
 def get_readings_with_metadata(start, end, region):
     params = {
         'dateRangeStart': parse_date(start),
         'dateRangeEnd': parse_date(end),
         'region': region
     }

     """
     Get gauge readings and metadata.
     Parameters
     ----------
     start: str, date, datetime, Timestamp
     end: str, date, datetime, Timestamp
     region: dict
         See example dicts CIRCLE_NEAR_UA and BOX_NEAR_UA for format.
     Returns
     -------
     readings_revisions: DataFrame
         Tidy rainlog data with columns:
         'gaugeId', 'gaugeRevisionId', 'quality', 'rainAmount', 'readingDate',
         'readingHour', 'readingId', 'readingMinute', 'remarks',
         'snowAccumulation', 'snowDepth', 'brand', 'createdDate', 'description',
         'gaugeType', 'gaugeTypeOther', 'model', 'position'
     """
     readings = get_readings(start, end, region)
     readings_df = pd.read_json(readings)
     revision_ids = readings_to_gauge_revision_ids(readings_df)
     revisions = get_gauge_revisions(revision_ids, start, end, region)
     revisions_df = pd.read_json(revisions)
     latlon = pd.DataFrame(revisions_df['position'].tolist())
     revisions_df = revisions_df.merge(latlon, left_index=True,
                                       right_index=True, how='inner')
     # don't need these duplicated columns
     revisions_df = revisions_df.drop(['position', 'gaugeId'], axis='columns')
     readings_revisions = readings_df.merge(revisions_df,
                                            on='gaugeRevisionId',
                                            how='inner')
     return readings_revisions
 
 
 def to_dataframe(json_bytes):
     """
     Convert API response to pandas DataFrame. Input must be in bytes.
     Do not call response.json() before passing in the data.
     Unless expanded to include date parsing, easier to just call
     pd.read_json() in a script.
     """
     df = pd.read_json(json_bytes)
     return df
 
 
 if __name__ == '__main__':
     parser = argparse.ArgumentParser(
         description='get data from the rainlog API')
     parser.add_argument('start', help='start date in YYYYMMDD format')
     parser.add_argument('end', help='start date in YYYYMMDD format')
     parser.add_argument(
         '--out', help='outfile path. default rainlog_{start}_{end}.csv')
     parser.add_argument(
         '--region',
         help='predefined region in this module (default: BOX_TUCSON)',
         default='BOX_TUCSON')
     args = parser.parse_args( )
 
     start = pd.Timestamp(args.start)
     end = pd.Timestamp(args.end)
     region = globals()[args.region]
 
     readings_revisions1 = get_readings_with_metadata(2015, 2020, 'BOX_FLAGSTAFF')
     readings_revisions2 = get_readings_with_metadata(2015, 2020, 'BOX_TUCSON')

     if args.out:
         outfile = args.out
     else:
         ftime = '%Y%m%d'
         outfile = f'rainlog_{region}_{start.strftime(ftime)}_{end.strftime(ftime)}.csv'
     readings_revisions1.to_csv(outfile)
     readings_revisions2.to_csv(outfile)