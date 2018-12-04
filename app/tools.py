#
# Author: Xiyan Wang, z5151289
#
# Tool Functions
#
# distance:                     Calculate distance between two locations
# waverider_buoy_locations:     Generate geojson for waverider
# get_sites:                    Assign nearest tide observation site and nearest wave observation site to each boat ramp
# update_waverider_data:        Update waverider realtime data, coastal water forecast data and warning data
# coast_ranges:                 Generate coast ranges data
# get_coast_name:               Get coast name with coordinates. Argument ranges is the return value of coast_ranges()
# get_datetime_from_str:        Convert tide time string to datetime
# around_time:                  If dt_input is within [-h hour, h hour] range of dt_cmp
#

from math import radians, cos, sin, asin, sqrt
import csv, json, requests, ftplib
from time import strptime
from datetime import datetime, timedelta
from xml.etree import ElementTree as et

wind_warning = {'Byron Coast': None, 'Coffs Coast': None, 'Macquarie Coast': None, 'Hunter Coast': None,
                'Sydney Coast': None, 'Illawarra Coast': None, 'Batemans Coast': None, 'Eden Coast': None}
hazardous_surf_warning = {'Byron Coast': None, 'Coffs Coast': None, 'Macquarie Coast': None, 'Hunter Coast': None,
                'Sydney Coast': None, 'Illawarra Coast': None, 'Batemans Coast': None, 'Eden Coast': None}

# Calculate distance between two locations (km)
def distance(lo1, la1, lo2, la2):
    lo1, la1, lo2, la2 = map(radians, [lo1, la1, lo2, la2])
    dlo = lo2 - lo1
    dla = la2 - la1
    a = sin(dla / 2) ** 2 + cos(la1) * cos(la2) * (sin(dlo / 2) ** 2)
    c = 2 * asin(sqrt(a))
    r = 6371
    return round(c * r, 1)

# Generate geojson for waverider
def waverider_buoy_locations():
    """
    {
      "type": "FeatureCollection",
      "features": [
        {
          "type": "Feature",
          "geometry": {"type": "Point", "coordinates": [153.694167, -28.870556]},
          "properties": {"id": 1, "name": "Byron Bay", "coordinates": [153.694167, -28.870556]}
        },
        {
          "type": "Feature",
          "geometry": {"type": "Point", "coordinates": [153.269167, -30.3625]},
          "properties": {"id": 2, "name": "Coffs Harbour", "coordinates": [153.269167, -30.3625]}
        },
        ...
    }
    """
    waveriders_geojson = {}
    with open('../data/waverider_buoy_location.csv', 'r') as f:
        data = csv.reader(f)
        i = 1
        features = []
        waveriders_geojson['type'] = 'FeatureCollection'
        waveriders_geojson['features'] = features
        for e in data:
            feature = {}
            geometry = {}
            wr = {}
            wr['id'] = i
            wr['name'] = e[0]
            la = e[1].split()
            lo = e[2].split()
            wr['coordinations'] = [round(int(lo[0]) + int(lo[1]) / 60 + int(lo[2]) / 3600, 6),
                                   -round((int(la[0]) + int(la[1]) / 60 + int(la[2]) / 3600), 6)]
            geometry['type'] = 'Point'
            geometry['coordinations'] = wr['coordinations']
            feature['type'] = 'Feature'
            feature['geometry'] = geometry
            feature['properties'] = wr
            features.append(feature)
            i += 1
    return waveriders_geojson

# Assign nearest tide observation site and nearest wave observation site to each boat ramp
def get_sites():
    """
    {
                'coordinates': [152.5082, -32.174],
                'name': 'Forster',
                'distance': 9.2
            },
            'waverider': {
                'id': 3,
                'coordinates': [152.856111, -31.813889],
                'name': 'Crowdy Head',
                'distance': 48.3
            }
        },
        ...
    }
    """
    with open('../data/boat_ramp_data_nsw.geojson', 'r') as boatramp:
        boatramp_data = json.loads(boatramp.read())
    with open('../data/tide_prediction_sites_nsw.geojson', 'r') as tide:
        tides_data = json.loads(tide.read())
    with open('../data/waverider_buoy_nsw.geojson', 'r') as waverider:
        waverider_data = json.loads(waverider.read())
    res = {}
    for br in boatramp_data['features']:
        br_lo, br_la = br['geometry']['coordinates']
        tide_distance = float('inf')
        waverider_distance = float('inf')
        tide_site = None
        waverider_site = None
        for t in tides_data['features']:
            t_lo, t_la = t['geometry']['coordinates']
            d = distance(br_lo, br_la, t_lo, t_la)
            if d < tide_distance:
                tide_distance = d
                tide_site = t
        for wr in waverider_data['features']:
            wr_lo, wr_la = wr['geometry']['coordinates']
            d = distance(br_lo, br_la, wr_lo, wr_la)
            if d < waverider_distance:
                waverider_distance = d
                waverider_site = wr
        tide = {}
        tide['aac'] = tide_site['properties']['AAC']
        tide['coordinates'] = tide_site['geometry']['coordinates']
        tide['name'] = tide_site['properties']['PORT_NAME']
        tide['distance'] = tide_distance
        waverider = {}
        waverider['id'] = waverider_site['properties']['id']
        waverider['coordinates'] = waverider_site['geometry']['coordinates']
        waverider['name'] = waverider_site['properties']['name']
        waverider['distance'] = waverider_distance
        tide['distance'] = tide_distance
        waverider['distance'] = waverider_distance
        br_dict = {}
        br_dict['is_near_ocean'] = tide_distance < 32
        br_dict['tide'] = tide
        br_dict['waverider'] = waverider
        res[br['properties']['cartodb_id']] = br_dict
    return res

# Update waverider realtime data, coastal water forecast data and warning data
def update_waverider_data():
    base_url = 'http://new.mhl.nsw.gov.au/data/realtime/timeseries/'
    wave_height = requests.get(base_url + 'NSW.WaveHeight.csv.dat.txt').content
    sea_temp = requests.get(base_url + 'NSWOffshoreWave.SeaTemp.csv.dat.txt').content
    with open('../data/wave_height.csv', 'wb') as f:
        f.write(wave_height)
    with open('../data/sea_temp.csv', 'wb') as f:
        f.write(sea_temp)
    ftp = ftplib.FTP('ftp.bom.gov.au')
    ftp.login()
    ftp.cwd('anon/gen/fwo')
    with open('../data/coastal_water.xml', 'wb') as f:
        ftp.retrbinary('RETR IDN11000.xml', f.write)
    global wind_warning
    global hazardous_surf_warning
    for key in wind_warning:
        wind_warning[key] = None
    for key in hazardous_surf_warning:
        hazardous_surf_warning[key] = None
    if 'IDN20400.xml' in ftp.nlst():
        with open('../data/wind_warning.xml', 'wb') as f:
            ftp.retrbinary('RETR IDN20400.xml', f.write)
        with open('../data/wind_warning.xml', 'r') as f:
            wind_warning_xml = et.fromstring(f.read()).find('warning').find('area')
            for period in wind_warning_xml:
                if period.get('index'):
                    time = period.get('start-time-local').split('T')[0]
                    for hazard in period:
                        warning_areas = []
                        warning_phenomena = None
                        for child in hazard:
                            if child.get('type') == 'warning_areas':
                                warning_areas = [e for e in wind_warning if child.text.find(e) != -1]
                            elif child.get('type') == 'warning_phenomena':
                                warning_phenomena = child.text
                        if warning_phenomena and warning_areas and warning_phenomena.lower().find('cancel') == -1:
                            for area in warning_areas:
                                if wind_warning[area] is None:
                                    wind_warning[area] = {}
                                wind_warning[area][time] = warning_phenomena
    if 'IDN28522.xml' in ftp.nlst():
        with open('../data/hazardous_surf_warning.xml', 'wb') as f:
            ftp.retrbinary('RETR IDN28522.xml', f.write)
        with open('../data/hazardous_surf_warning.xml', 'r') as f:
            hazardous_surf_warning_xml = et.fromstring(f.read()).find('warning').find('area')
            for period in hazardous_surf_warning_xml:
                if period.get('index'):
                    time = period.get('start-time-local').split('T')[0]
                    for hazard in period:
                        warning_areas = []
                        warning_phenomena = None
                        for child in hazard:
                            if child.get('type') == 'warning_areas':
                                warning_areas = [e for e in hazardous_surf_warning if child.text.find(e) != -1]
                            elif child.get('type') == 'warning_phenomena':
                                warning_phenomena = child.text
                        if warning_phenomena and warning_areas and warning_phenomena.lower().find('cancel') == -1:
                            for area in warning_areas:
                                if hazardous_surf_warning[area] is None:
                                    hazardous_surf_warning[area] = {}
                                hazardous_surf_warning[area][time] = warning_phenomena
    ftp.close()

# Generate coast ranges data
def coast_ranges():
    '''
    :return:
    [{'name': 'Byron Coast', 'latitude_range': (-29.8297059, -28.1642813)},
    {'name': 'Coffs Coast', 'latitude_range': (-30.9236771, -29.8297059)},
    {'name': 'Macquarie Coast', 'latitude_range': (-32.4225347, -30.9236771)},
    {'name': 'Hunter Coast', 'latitude_range': (-33.5522768, -32.4225347)},
    {'name': 'Sydney Coast', 'latitude_range': (-34.063371, -33.5522768)},
        1426: {
            'is_near_ocean': True,
            'tide': {
                'aac': 'NSW_TP018',
    {'name': 'Illawarra Coast', 'latitude_range': (-35.3560721, -34.063371)},
    {'name': 'Batemans Coast', 'latitude_range': (-36.2512024, -35.3560721)},
    {'name': 'Eden Coast', 'latitude_range': (-37.5590499, -36.2512024)}]
    '''
    coastal_areas = ['Byron Coast', 'Coffs Coast', 'Macquarie Coast', 'Hunter Coast',
                     'Sydney Coast', 'Illawarra Coast', 'Batemans Coast', 'Eden Coast']
    with open('../data/coastal_areas.csv', 'r') as f:
        data = list(csv.reader(f))
    return [{'name': coastal_areas[i], 'latitude_range': (float(data[i + 1][2]), float(data[i][2]))} for i in range(len(coastal_areas))]

# Get coast name with coordinates. Argument ranges is the return value of coast_ranges()
def get_coast_name(coordinates, ranges):
    la = coordinates[1]
    for coast in ranges:
        if la > coast['latitude_range'][0]:
            return coast['name']

# Convert tide time string to datetime. Other information is provided by datetime object dt
def get_datetime_from_str(s, dt):
    '''
    :param s: '1:43 AM'
    :param dt: datetime object datetime(2018, 5, 16, 23, 3, 7, 61555)
    :return: datetime(2018, 5, 16, 1, 43, 7, 61555)
    '''
    t = strptime(s, '%I:%M %p')
    return datetime(dt.year, dt.month, dt.day, t.tm_hour, t.tm_min, dt.second, dt.microsecond)

# If dt_input is within [-h hour, h hour] range of dt_cmp
def around_time(dt_input, dt_cmp, h=1):
    '''
    :param dt_input: datetime(2018, 5, 16, 23, 3, 7, 61555)
    :param dt_cmp: datetime(2018, 5, 16, 1, 43, 7, 61555)
    :param h: 1
    :return: False
    '''
    lower_bound = dt_cmp - timedelta(hours=h)
    upper_bound = dt_cmp + timedelta(hours=h)
    if dt_input > lower_bound and dt_input < upper_bound:
        return True
    return False