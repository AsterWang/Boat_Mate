#
# Author: Xiyan Wang, z5151289
#
# For Safety Analysis API
#

from app.tools import *
import pytz


def get_tide(tide, safety_score, now, waterway_access):
    tide_sorted = sorted(tide['data'], key=lambda x: x['height'])
    if len(tide_sorted) == 4:
        low_tide_time1 = get_datetime_from_str(tide_sorted[0]['time'], now)
        low_tide_time2 = get_datetime_from_str(tide_sorted[1]['time'], now)
        low_tide_time = low_tide_time1 if abs(now - low_tide_time1) < abs(now - low_tide_time2) else low_tide_time2
        high_tide_time1 = get_datetime_from_str(tide_sorted[2]['time'], now)
        high_tide_time2 = get_datetime_from_str(tide_sorted[3]['time'], now)
        high_tide_time, high_tide = (high_tide_time1, tide_sorted[2]['height']) \
            if abs(now - high_tide_time1) < abs(now - high_tide_time2) else (high_tide_time2, tide_sorted[3]['height'])
    elif tide['data'][0]['height'] > tide['data'][1]['height']:
        high_tide_time1 = get_datetime_from_str(tide['data'][0]['time'], now)
        high_tide_time2 = get_datetime_from_str(tide['data'][2]['time'], now)
        high_tide_time, high_tide = (high_tide_time1, tide['data'][0]['height']) \
            if abs(now - high_tide_time1) < abs(now - high_tide_time2) else (high_tide_time2, tide['data'][2]['height'])
        low_tide_time = get_datetime_from_str(tide['data'][1]['time'], now)
    else:
        low_tide_time1 = get_datetime_from_str(tide['data'][0]['time'], now)
        low_tide_time2 = get_datetime_from_str(tide['data'][2]['time'], now)
        low_tide_time = low_tide_time1 if abs(now - low_tide_time1) < abs(now - low_tide_time2) else low_tide_time2
        high_tide_time, high_tide = get_datetime_from_str(tide['data'][1]['time'], now), tide['data'][1]['height']
    if waterway_access.find('High Tide Only') != -1:
        if around_time(now, low_tide_time, 1):
            tide['info'] = 'Boat Ramp Not Accessable'
            safety_score -= 8
        elif around_time(now, low_tide_time, 2):
            tide['info'] = 'Boat Ramp Probably Not Accessable'
            safety_score -= 5
        elif not around_time(now, high_tide_time, 2) or high_tide < 0.8:
            tide['info'] = 'Boat Ramp May Not Be Accessable'
            safety_score -= 3
        elif not around_time(now, high_tide_time, 1):
            tide['info'] = 'Boat Ramp May Not Be Accessable'
            safety_score -= 1
        else:
            tide['info'] = 'Safe'
    else:
        if around_time(now, low_tide_time, 1):
            tide['info'] = 'Low Tide'
            safety_score -= 1
        else:
            tide['info'] = 'Safe'
    return tide, safety_score

def get_waverider(waverider, safety_score):
    waverider_data = {}
    with open('../data/wave_height.csv', 'r') as f:
        data = list(csv.reader(f))
        for line in data[::-1]:
            wave_height = line[waverider['id']]
            if wave_height != '':
                wave_height = float(wave_height)
                wave_height_data = {'time': line[0], 'data': wave_height}
                if wave_height > 6:
                    wave_height_data['info'] = 'Huge Wave'
                    safety_score -= 10
                elif wave_height > 4:
                    wave_height_data['info'] = 'Strong Wave'
                    safety_score -= 5
                elif wave_height > 2.5:
                    wave_height_data['info'] = 'Moderate to Strong Wave'
                    safety_score -= 3
                elif wave_height > 1.25:
                    wave_height_data['info'] = 'Moderate Wave'
                    safety_score -= 1
                else:
                    wave_height_data['info'] = 'Safe'
                waverider_data['wave_height'] = wave_height_data
                break
    with open('../data/sea_temp.csv', 'r') as f:
        data = list(csv.reader(f))
        for line in data[::-1]:
            sea_temp = line[waverider['id']]
            if sea_temp != '':
                sea_temp = float(sea_temp)
                sea_temp_data = {'time': line[0], 'data': sea_temp}
                if sea_temp < 15:
                    sea_temp_data['info'] = 'Low Sea Temperature'
                    safety_score -= 2
                else:
                    sea_temp_data['info'] = 'Safe'
                waverider_data['sea_temp'] = sea_temp_data
                break
    waverider['data'] = waverider_data
    return waverider, safety_score

def get_coastal_waters(safety_score, now, coast):
    coastal_waters_info = []
    with open('../data/coastal_water.xml', 'r') as f:
        coastal_waters_xml = et.fromstring(f.read()).find('forecast')
    for area in coastal_waters_xml:
        if area.get('description').split(':')[0] == coast:
            for period in area:
                dt_str = period.get('start-time-local').split('+')[0]
                dt = datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%S')
                if dt.day >= now.day:
                    coast_waters_day_info = {}
                    coast_waters_day_info['date'] = dt_str.split('T')[0]
                    for info in period:
                        coast_waters_day_info[info.get('type')] = info.text
                    coastal_waters_info.append(coast_waters_day_info)
    return coastal_waters_info, safety_score

def get_warning(safety_score, now, coast):
    warning = {}
    if hazardous_surf_warning[coast] is not None:
        warning['hazadous_surf'] = hazardous_surf_warning[coast]
        if now.strftime('%Y-%m-%d') in hazardous_surf_warning[coast]:
            safety_score -= 8
    if wind_warning[coast] is not None:
        warning['wind'] = wind_warning[coast]
        if now.strftime('%Y-%m-%d') in wind_warning[coast]:
            safety_score -= 8
    return warning, safety_score

def get_wind(safety_score, weather_xml):
    wind_xml = weather_xml.find('wind')
    wind = {}
    wind_data = {}
    wind['info'] = wind_xml.find('speed').get('name')
    wind_data['speed'] = float(wind_xml.find("speed").get("value"))
    wind_data['direction_degree'] = float(wind_xml.find("direction").get("value"))
    wind_data['direction_name'] = wind_xml.find("direction").get("name")
    wind_data['direction_code'] = wind_xml.find("direction").get("code")
    wind['data'] = wind_data
    # Strong wind (>= 26 knots)
    if wind_data['speed'] > 13.9:
        safety_score -= 10
    # Strong breeze
    elif wind_data['speed'] >= 10.8:
        safety_score -= 5
    # Fresh breeze
    elif wind_data['speed'] >= 8:
        safety_score -= 3
    # Moderate breeze
    elif wind_data['speed'] >= 5.5:
        safety_score -= 1
    return wind, safety_score

def get_daytime(safety_score, now, weather_xml):
    sun_rise = weather_xml.find('city').find('sun').get('rise')
    sun_set = weather_xml.find('city').find('sun').get('set')
    sun_rise = datetime.strptime(sun_rise, '%Y-%m-%dT%H:%M:%S')
    sun_rise = pytz.utc.localize(sun_rise).astimezone(pytz.timezone('Australia/Sydney'))
    sun_set = datetime.strptime(sun_set, '%Y-%m-%dT%H:%M:%S')
    sun_set = pytz.utc.localize(sun_set).astimezone(pytz.timezone('Australia/Sydney'))
    now = pytz.timezone('Australia/Sydney').localize(now)
    if now > sun_rise and now < sun_set:
        daytime_info = 'Daytime'
    else:
        daytime_info = 'Night'
        safety_score -= 3
    return daytime_info, sun_rise, sun_set, safety_score

def get_weather_info(safety_score, weather_xml):
    code = int(weather_xml.find('weather').get('number'))
    weather_info = weather_xml.find('weather').get('value')
    if code == 800:
        pass
    elif code // 100 == 8 and code % 100 < 3:  # Light cloud
        safety_score -= 1
    elif code // 100 == 8:  # Heavy cloud
        safety_score -= 2
    elif code // 100 == 3:  # Drizzle
        safety_score -= 4
    else:  # Other
        safety_score -= 10
    return weather_info, safety_score

def get_temperature(safety_score, weather_xml):
    temp = {}
    temp_degree = round(float(weather_xml.find('temperature').get('value')) - 273.15, 1)
    if temp_degree < 5:
        temp_info = 'Freezing'
        safety_score -= 8
    elif temp_degree < 10:
        temp_info = 'Cold'
        safety_score -= 5
    elif temp_degree < 15:
        temp_info = 'Chilly'
        safety_score -= 3
    elif temp_degree < 20:
        temp_info = 'Cool'
        safety_score -= 1
    elif temp_degree > 35:
        temp_info = 'Hot'
        safety_score -= 3
    elif temp_degree > 30:
        temp_info = 'Warm'
        safety_score -= 1
    else:
        temp_info = 'Comfortable'
    temp['data'] = temp_degree
    temp['info'] = temp_info
    return temp, safety_score