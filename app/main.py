#
# Author: Xiyan Wang, z5151289 (boatramps APIs, safetyanalysis API)
#         Pengyan Rao, z5099703 (weather API, route: /test)
#

from flask import Flask, jsonify, request, render_template
from mongoengine import connect
from mongoengine.queryset.visitor import Q
from flask_cors import CORS
from app.database import BoatRamps, Tides, BoatRampsSmall
from app.safety_analysis import *
from datetime import date
from threading import Timer
from app.get_weather_data import get_weather_data

conn = connect('comp9321_ass3', host='mongodb://deanna:deanna@ds123770.mlab.com:23770/comp9321_ass3',
                    username='deanna', password='deanna')

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("front_end.html")


# Get all boat ramps
@app.route('/boatramps', methods=['GET'])
def boat_ramps_all ():
    '''
    :return: geojson
    {
        "features": [
            {
                "geometry": {
                    "coordinates": [
                        152.469059,
                        -32.098654
                    ],
                    "type": "Point"
                },
                "properties": {
                    "asset_owner": "Great Lakes Council",
                    "boat_ramp_name": "Wallamba River - Shalimar Boat Ramp, Darawank",
                    "car_spaces": "0-10",
                    "contact_number": "02 6591 7222",
                    "has_bbq": false,
                    "has_bins": false,
                    "has_fee_payable": false,
                    "has_fish_cleaning_table": false,
                    "has_fuel": false,
                    "has_kiosk": false,
                    "has_lighting": false,
                    "has_pontoon_nearby": false,
                    "has_pontoon_ramp": false,
                    "has_toilets": false,
                    "id": 1426,
                    "is_near_ocean": true,
                    "number_ramp_lanes": "1",
                    "postcode": 2428,
                    "ramp_condition": "GOOD",
                    "ramp_material": "Concrete",
                    "street": "Aquatic Road",
                    "suburb": "Darawank",
                    "waterway_access": "All Times",
                    "waterway_name": "Wallamba River"
                },
                "type": "Feature"
            },
            ...
        ],
        "type": "FeatureCollection"
    }
    '''

    feature_collection = {'type': 'FeatureCollection'}
    features = []
    for boatramp in BoatRamps.objects:
        feature = {'type': 'Feature'}
        feature['geometry'] = {'type': 'Point', 'coordinates': boatramp.coordinates}
        feature['properties'] = json.loads(boatramp.properties.to_json())
        if boatramp.properties.is_near_ocean == True:
            features.append(feature)
    feature_collection['features'] = features
    return jsonify(feature_collection), 200

# Get all boat ramps from a small collection for test use
@app.route('/boatramps/test', methods=['GET'])
def boat_ramps_all_small ():
    '''
    :return: geojson
    {
        "features": [
            {
                "geometry": {
                    "coordinates": [
                        152.469059,
                        -32.098654
                    ],
                    "type": "Point"
                },
                "properties": {
                    "asset_owner": "Great Lakes Council",
                    "boat_ramp_name": "Wallamba River - Shalimar Boat Ramp, Darawank",
                    "car_spaces": "0-10",
                    "contact_number": "02 6591 7222",
                    "has_bbq": false,
                    "has_bins": false,
                    "has_fee_payable": false,
                    "has_fish_cleaning_table": false,
                    "has_fuel": false,
                    "has_kiosk": false,
                    "has_lighting": false,
                    "has_pontoon_nearby": false,
                    "has_pontoon_ramp": false,
                    "has_toilets": false,
                    "id": 1426,
                    "is_near_ocean": true,
                    "number_ramp_lanes": "1",
                    "postcode": 2428,
                    "ramp_condition": "GOOD",
                    "ramp_material": "Concrete",
                    "street": "Aquatic Road",
                    "suburb": "Darawank",
                    "waterway_access": "All Times",
                    "waterway_name": "Wallamba River"
                },
                "type": "Feature"
            },
            ...
        ],
        "type": "FeatureCollection"
    }
    '''
    feature_collection = {'type': 'FeatureCollection'}
    features = []
    for boatramp in BoatRampsSmall.objects:
        feature = {'type': 'Feature'}
        feature['geometry'] = {'type': 'Point', 'coordinates': boatramp.coordinates}
        feature['properties'] = json.loads(boatramp.properties.to_json())
        if boatramp.properties.is_near_ocean == True:
            features.append(feature)
    feature_collection['features'] = features
    return jsonify(feature_collection), 200

# Get boat ramps with specified facilities
# Sample: http://127.0.0.1:5000/boatramps/filter?has_bbq and has_toilets
@app.route('/boatramps/filter', methods=['GET'])
def boat_ramps_filtered():
    '''
    :return: geojson, same as boat_ramps_all
    '''

    args = list(request.args.keys())
    if not args:
        return jsonify(info='Filter is empty'), 400
    facilities = [e.strip() for e in args[0].split('and')]
    facilities_set = {'has_bbq', 'has_bins', 'has_fee_payable', 'has_fish_cleaning_table', 'has_fuel',
                      'has_kiosk', 'has_lighting', 'has_pontoon_nearby', 'has_pontoon_ramp', 'has_toilets'}
    if any([facility not in facilities_set for facility in facilities]):
        return jsonify(info='Invalid filter'), 400
    q = None
    for facility in facilities:
        if facility == 'has_bbq':
            q = Q(properties__has_bbq=True) if q is None else q & Q(properties__has_bbq=True)
        elif facility == 'has_bins':
            q = Q(properties__has_bins=True) if q is None else q & Q(properties__has_bins=True)
        elif facility == 'has_fee_payable':
            q = Q(properties__has_fee_payable=True) if q is None else q & Q(properties__has_fee_payable=True)
        elif facility == 'has_fish_cleaning_table':
            q = Q(properties__has_fish_cleaning_table=True) if q is None else q & Q(properties__has_fish_cleaning_table=True)
        elif facility == 'has_fuel':
            q = Q(properties__has_fuel=True) if q is None else q & Q(properties__has_fuel=True)
        elif facility == 'has_kiosk':
            q = Q(properties__has_kiosk=True) if q is None else q & Q(properties__has_kiosk=True)
        elif facility == 'has_lighting':
            q = Q(properties__has_lighting=True) if q is None else q & Q(properties__has_lighting=True)
        elif facility == 'has_pontoon_nearby':
            q = Q(properties__has_pontoon_nearby=True) if q is None else q & Q(properties__has_pontoon_nearby=True)
        elif facility == 'has_pontoon_ramp':
            q = Q(properties__has_pontoon_ramp=True) if q is None else q & Q(properties__has_pontoon_ramp=True)
        elif facility == 'has_toilets':
            q = Q(properties__has_toilets=True) if q is None else q & Q(properties__has_toilets=True)
    feature_collection = {'type': 'FeatureCollection'}
    features = []
    for boatramp in BoatRamps.objects(q):
        feature = {'type': 'Feature'}
        feature['geometry'] = {'type': 'Point', 'coordinates': boatramp.coordinates}
        feature['properties'] = json.loads(boatramp.properties.to_json())
        features.append(feature)
    feature_collection['features'] = features
    return jsonify(feature_collection), 200

# Get safety analysis
@app.route('/boatramps/safetyanalysis/<boatramp_id>', methods=['GET'])
def boat_ramps_safety_analysis(boatramp_id):
    '''
    :param boatramp_id: 1666
    :return: json
    {
        "coast": "Eden Coast",
        "coast_waters": [
            {
                "date": "2018-05-21",
                "forecast_caution": "Surf conditions may be more powerful than they appear and are expected to be hazardous for coastal activities such as crossing bars by boat and rock fishing.",
                "forecast_seas": "2 to 3 metres, increasing to 3 to 5 metres offshore south of Merimbula.",
                "forecast_swell1": "Southerly 1 to 1.5 metres inshore, increasing to 1.5 to 2.5 metres offshore.",
                "forecast_weather": "Partly cloudy.",
                "forecast_winds": "Southwesterly 20 to 30 knots, reaching 35 knots offshore south of Merimbula."
            },
            {
                "date": "2018-05-22",
                "forecast_seas": "2 to 3 metres, increasing to 3 to 5 metres offshore south of Merimbula.",
                "forecast_swell1": "Southerly 1.5 to 2.5 metres, increasing to 2 to 4 metres offshore.",
                "forecast_weather": "Partly cloudy.",
                "forecast_winds": "West to southwesterly 20 to 30 knots, reaching 35 knots offshore south of Merimbula."
            },
            {
                "date": "2018-05-23",
                "forecast_caution": "Large and powerful surf conditions are expected to be hazardous for coastal activities such as crossing bars by boat and rock fishing.",
                "forecast_seas": "2 to 3 metres, increasing to 2.5 to 4 metres offshore south of Green Cape.",
                "forecast_swell1": "Southerly 3 to 4 metres, decreasing to 2 to 3 metres during the morning.",
                "forecast_weather": "Partly cloudy.",
                "forecast_winds": "West to southwesterly 20 to 30 knots."
            }
        ],
        "daytime": "Daytime",
        "safety_score": 0,
        "sunrise": "Mon, 21 May 2018 06:56:48 GMT",
        "sunset": "Mon, 21 May 2018 16:57:02 GMT",
        "temperature": {
            "data": 16.3,
            "info": "Cool"
        },
        "tide": {
            "aac": "NSW_TP002",
            "coordinates": [
                149.9083,
                -37.0712
            ],
            "data": [
                {
                    "height": 1.81,
                    "time": "12:29 AM"
                },
                {
                    "height": 0.37,
                    "time": "7:33 AM"
                },
                {
                    "height": 1.4,
                    "time": "1:53 PM"
                },
                {
                    "height": 0.79,
                    "time": "7:17 PM"
                }
            ],
            "distance": 2.2,
            "info": "Safe",
            "name": "Eden"
        },
        "warning": {
            "hazadous_surf": {
                "2018-05-21": "Hazardous Surf Warning"
            },
            "wind": {
                "2018-05-21": "Gale Warning",
                "2018-05-22": "Gale Warning"
            }
        },
        "waverider": {
            "coordinates": [
                150.193333,
                -37.265833
            ],
            "data": {
                "sea_temp": {
                    "data": 16.7,
                    "info": "Safe",
                    "time": "2018-05-21 13:00:00"
                },
                "wave_height": {
                    "data": 2.316,
                    "info": "Moderate Wave",
                    "time": "2018-05-21 13:00:00"
                }
            },
            "distance": 34.4,
            "id": 7,
            "name": "Eden"
        },
        "weather": "clear sky",
        "wind": {
            "data": {
                "direction_code": "SW",
                "direction_degree": 236.002,
                "direction_name": "Southwest",
                "speed": 8.17
            },
            "info": "Fresh Breeze"
        }
    }
    '''

    if not boatramp_id.isdigit():
        return jsonify(info='Invalid id'), 404
    boat_ramp = BoatRamps.objects(Q(id=boatramp_id))
    safety_score = 10
    if not boat_ramp:
        return jsonify(info='Invalid id'), 404
    coast = boat_ramp[0].coast
    if not boat_ramp[0].properties.is_near_ocean:
        return jsonify(info='Not coastal'), 400
    tide = json.loads(boat_ramp[0].tide.to_json())
    waverider = json.loads(boat_ramp[0].waverider.to_json())
    now = datetime.now()
    base_url = 'http://api.openweathermap.org/data/2.5/weather'
    weather_xml = et.fromstring(requests.get(base_url + f'?lat={boat_ramp[0].coordinates[1]}&'
        f'lon={boat_ramp[0].coordinates[0]}&APPID=33309ed9e9632b6938cefbda6bb2139d&mode=xml').content.decode('utf-8'))

    # Tide (mongodb)
    tide['data'] = json.loads(Tides.objects(Q(id__aac__iexact=tide['aac']) &
                                            Q(id__date=date.today().toordinal()))[0].to_json())['tide_data']
    tide, safety_score = get_tide(tide, safety_score, now, boat_ramp[0].properties.waterway_access)

    # Waverider: Wave, Sea Temperature (realtime files downloaded every 30 minutes)
    waverider, safety_score = get_waverider(waverider, safety_score)

    # Coastal Waters Forecast Information (realtime files downloaded every 30 minutes)
    coastal_waters_info, safety_score = get_coastal_waters(safety_score, now, coast)

    # Warning (realtime files downloaded every 30 minutes)
    warning, safety_score = get_warning(safety_score, now, coast)

    # Wind (openweathermap api)
    wind, safety_score = get_wind(safety_score, weather_xml)

    # Daytime: (openweathermap api)
    daytime_info, sun_rise, sun_set, safety_score = get_daytime(safety_score, now, weather_xml)

    # Weather: (openweathermap api)
    weather_info, safety_score = get_weather_info(safety_score, weather_xml)

    # Temperature: (openweathermap api)
    temp, safety_score = get_temperature(safety_score, weather_xml)

    safety_score = safety_score if safety_score > 0 else 0
    return jsonify(coast=coast, tide=tide, waverider=waverider, wind=wind, weather=weather_info, temperature=temp,
                   coast_waters=coastal_waters_info, daytime=daytime_info, sunset=sun_set, sunrise=sun_rise,
                   warning=warning, safety_score=safety_score), 200

@app.route('/weather', methods=['GET'])
def weather():
    """
    return: weather info

        type: json

        1. weather (ref: https://openweathermap.org/current)

            {"coord":{"lon":139,"lat":35},
            "sys":{"country":"JP","sunrise":1369769524,"sunset":1369821049},
            "weather":[{"id":804,"main":"clouds","description":"overcast clouds","icon":"04n"}],
            "main":{"temp":289.5,"humidity":89,"pressure":1013,"temp_min":287.04,"temp_max":292.04},
            "wind":{"speed":7.31,"deg":187.002},
            "rain":{"3h":0},
            "clouds":{"all":92},
            "dt":1369824698,
            "id":1851632,
            "name":"Shuzenji",
            "cod":200}

        2. forecast (5 day weather forecast)

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
    """
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    current, forecast, uvi = get_weather_data(lat, lon)
    if current is None:
        return jsonify(success='false'), 400

    # Current weather info
    current_return = {}
    current_return['temp'] = current['main']['temp']
    current_return['temp_max'] = current['main']['temp_max']
    current_return['temp_min'] = current['main']['temp_min']
    current_return['humidity'] = current['main']['humidity']
    current_return['pressure'] = current['main']['pressure']
    current_return['condition'] = current['weather'][0]['main']
    current_return['description'] = current['weather'][0]['description']
    current_return['icon'] = current['weather'][0]['icon']

    # UV Index
    uvi_return = uvi['value']

    # Next five days forecast
    forecast_return = forecast

    return jsonify(success='success', today_weather=current_return, forecast=forecast_return, uvi=uvi_return), 200


@app.route('/apitest', methods=['GET'])
def api_test():
    """
    For debugging
    Please don't delete it.
    """
    return render_template('test.html')


if __name__ == '__main__':
    update_waverider_data()
    Timer(60 * 30, update_waverider_data).start() # Update waverider data every 30 minutes
    app.run()
    conn.close()
