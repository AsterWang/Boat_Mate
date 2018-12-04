#
# Author: Pengyan Rao, z5099703
#

import requests, json


def check_para(s):
    try:
        nb = float(s)
        nb = round(nb, 1)
        # nb = int(nb)
        # if nb < 0:
        return nb
    except:
        print(f'Illegal input: {s}!')
        return None


def get_weather_data(latitude, longitude):
    """
    API limit: Calls per minute (no more than) 60
    return:
            json object
            1.today weather
            2.forecast(5 days/3 hour forecast)
            3.uv index
    """

    # api.openweathermap.org/data/2.5/weather?lat=35&lon=139
    # api.openweathermap.org/data/2.5/forecast?lat=35&lon=139

    latitude = check_para(latitude)
    longitude = check_para(longitude)
    # print(f'latitude: {latitude}  longitude: {longitude}')

    if latitude is None or longitude is None:
        print(f'Fail: weather!')
        return None, None

    url_today_weather = f'http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&APPID=c1f9ad70f406af481134a888249c42c7'
    # print(url_today_weather)
    response_today_weather = requests.get(url_today_weather)
    response_today_weather_data = json.loads(response_today_weather.content.decode())
    # print(response_today_weather_data)

    url_forecast = f'http://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&APPID=c1f9ad70f406af481134a888249c42c7'
    response_forecast = requests.get(url_forecast)
    response_forecast_data = json.loads(response_forecast.content.decode())
    # print(response_forecast_data)

    url_uvi = f'http://api.openweathermap.org/data/2.5/uvi?lat={latitude}&lon={longitude}&APPID=c1f9ad70f406af481134a888249c42c7'
    response_uvi = requests.get(url_uvi)
    response_uvi_data = json.loads(response_uvi.content.decode())
    # print(f'response uvi:{response_uvi_data}')

    return response_today_weather_data, processing_forecast(response_forecast_data), response_uvi_data


def processing_forecast(response_forecast):
    """
    From:
        {"city":{"id":1851632,"name":"Shuzenji",
                "coord":{"lon":138.933334,"lat":34.966671},
                "country":"JP",
                "cod":"200",
                "message":0.0045,
                "cnt":38,
                "list":[{
                        "dt":1406106000,
                        "main":{
                            "temp":298.77,
                            "temp_min":298.77,
                            "temp_max":298.774,
                            "pressure":1005.93,
                            "sea_level":1018.18,
                            "grnd_level":1005.93,
                            "humidity":87,
                            "temp_kf":0.26},
                        "weather":[{"id":804,"main":"Clouds","description":"overcast clouds","icon":"04d"}],
                        "clouds":{"all":88},
                        "wind":{"speed":5.71,"deg":229.501},
                        "sys":{"pod":"d"},
                        "dt_txt":"2014-07-23 09:00:00"}
                        ]}
    To:
        [ {"date":"2018-05-21",
            "temp":290.247,
            "temp_max":294.81,
            "temp_min":286.812,
            "weather":["Clear","Clouds"],
            "wind":{
                "deg":[246.501,264.503],
                "speed":[4.73,5.71]
                }
            }
        ]
    :param response_forecast
    :return: forecast (a list)
    """
    forecast = list()
    info = dict()
    days = []
    temp = []
    # print(response_forecast)
    for item in response_forecast['list']:

        date = item['dt_txt'].split(' ')[0]
        if date not in days:
            days.append(date)
            if len(temp) > 0:
                info['weather'] = weather
                info['temp'] = round(sum(temp) / len(temp), 1)
                info['temp_min'] = round(min(temp_min), 1)
                info['temp_max'] = round(max(temp_max), 1)
                info['wind'] = {'speed': [min(wind_speed), max(wind_speed)], 'deg': [min(wind_deg), max(wind_deg)]}
                info['date'] = days[-2]
                info['icon'] = item['weather'][0]['icon']
                forecast.append(info)
            info = dict()
            wind_speed = []
            wind_deg = []
            temp = []
            temp_min = []
            temp_max = []
            weather = []
        wind_speed.append(item['wind']['speed'])
        wind_deg.append(item['wind']['deg'])
        wt = item['weather'][0]['main']
        if wt not in weather:
            weather.append(wt)
        temp.append(item['main']['temp'])
        temp_min.append(item['main']['temp_min'])
        temp_max.append(item['main']['temp_max'])

    info['weather'] = weather
    info['temp'] = round(sum(temp) / len(temp), 1)
    info['temp_min'] = round(min(temp_min), 1)
    info['temp_max'] = round(max(temp_max), 1)
    info['wind'] = {'speed': [min(wind_speed), max(wind_speed)], 'deg': [min(wind_deg), max(wind_deg)]}
    info['date'] = days[-1]
    forecast.append(info)

    return forecast


if __name__ == '__main__':
    # get_weather_data(35, 139)
    response_today_weather_data, response_forecast_data, response_uvi_data = get_weather_data('35.1', 110.8)
    # print(response_uvi_data)
    # get_weather_data('35.1', '139.8a')
