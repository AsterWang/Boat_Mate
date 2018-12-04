#
# Author: Xiyan Wang, z5151289
#
# Three Collections: BoatRamps, BoatRampsSmall and Tides. Functions are offered to import data to mlab
#
# BoarRampsSmall, which only have 23 documents, is for test use
#

from mongoengine import connect, IntField, LongField, StringField, FloatField, \
    Document, EmbeddedDocument, ListField, EmbeddedDocumentField, BooleanField
from app.tools import *
from app.download_pdf import link_location_mapping, download_pdf
from app.extract_pdf_tide_data import get_pdf_data
from datetime import date, time
import os

# Boat ramp properties
class BoatRampProperties(EmbeddedDocument):
    id = IntField()
    boat_ramp_name = StringField(max_length=200)
    suburb = StringField(max_length=50)
    street = StringField(max_length=50)
    postcode = IntField()
    asset_owner = StringField(max_length=200)
    contact_number = StringField(max_length=20)
    waterway_name = StringField(max_length=50)
    waterway_access = StringField(max_length=50)
    car_spaces = StringField(max_length=20)
    number_ramp_lanes = StringField(max_length=20)
    ramp_condition = StringField(max_length=20)
    ramp_material = StringField(max_length=20)
    is_near_ocean = BooleanField()
    has_bbq = BooleanField()
    has_bins = BooleanField()
    has_fee_payable = BooleanField()
    has_fish_cleaning_table = BooleanField()
    has_fuel = BooleanField()
    has_kiosk = BooleanField()
    has_lighting = BooleanField()
    has_pontoon_nearby = BooleanField()
    has_pontoon_ramp = BooleanField()
    has_toilets = BooleanField()

    def __init__(self, id, boat_ramp_name=None, suburb=None, street=None, postcode=None, asset_owner=None, contact_number=None,
                 waterway_name=None, waterway_access=None, car_spaces=None, number_ramp_lanes=None, ramp_condition=None, ramp_material=None,
                 is_near_ocean=None, has_bbq=None, has_bins=None, has_fee_payable=None, has_fish_cleaning_table=None, has_fuel=None, has_kiosk=None,
                 has_lighting=None, has_pontoon_nearby=None, has_pontoon_ramp=None, has_toilets=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = id
        self.boat_ramp_name = boat_ramp_name
        self.suburb = suburb
        self.street = street
        self.postcode = postcode
        self.asset_owner = asset_owner
        self.contact_number = contact_number if contact_number else 'Not provided'
        self.waterway_name = waterway_name
        self.waterway_access = waterway_access
        self.car_spaces = car_spaces
        self.number_ramp_lanes = number_ramp_lanes if number_ramp_lanes else 'Not provided'
        self.ramp_condition = ramp_condition
        self.ramp_material = ramp_material
        self.is_near_ocean = is_near_ocean # True if distance to nearest tide prediction site < 32km
        self.has_bbq = has_bbq
        self.has_bins = has_bins
        self.has_fee_payable = has_fee_payable
        self.has_fish_cleaning_table = has_fish_cleaning_table
        self.has_fuel = has_fuel
        self.has_kiosk = has_kiosk
        self.has_lighting = has_lighting
        self.has_pontoon_nearby = has_pontoon_nearby
        self.has_pontoon_ramp = has_pontoon_ramp
        self.has_toilets = has_toilets

# Nearest observation site for tide data
class TidePredictionSite(EmbeddedDocument):
    aac = StringField(max_length=10)
    coordinates = ListField()
    name = StringField(max_length=50)
    distance = FloatField()

    def __init__(self, aac, coordinates, name, distance, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aac = aac
        self.coordinates = coordinates
        self.name = name
        self.distance = distance

# Nearest observation site for wave height and sea temperature data
class WaveriderBuoy(EmbeddedDocument):
    id = IntField()
    coordinates = ListField()
    name = StringField(max_length=50)
    distance = FloatField()

    def __init__(self, id, coordinates, name, distance, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = id
        self.coordinates = coordinates
        self.name = name
        self.distance = distance

# BoatRamps collection
class BoatRamps(Document):
    id = IntField(primary_key=True) # cartodb_id
    coordinates = ListField()
    properties = EmbeddedDocumentField(BoatRampProperties)
    tide = EmbeddedDocumentField(TidePredictionSite)
    waverider = EmbeddedDocumentField(WaveriderBuoy)
    coast = StringField(max_length=20)

    def __init__(self, id, coordinates, properties, tide, waverider, coast, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = id
        self.coordinates = coordinates
        self.properties = properties
        self.tide = tide
        self.waverider = waverider
        self.coast = coast

# BoatRampsSmall collection
# For test use
class BoatRampsSmall(Document):
    id = IntField(primary_key=True)  # cartodb_id
    coordinates = ListField()
    properties = EmbeddedDocumentField(BoatRampProperties)
    tide = EmbeddedDocumentField(TidePredictionSite)
    waverider = EmbeddedDocumentField(WaveriderBuoy)
    coast = StringField(max_length=20)

    def __init__(self, id, coordinates, properties, tide, waverider, coast, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = id
        self.coordinates = coordinates
        self.properties = properties
        self.tide = tide
        self.waverider = waverider
        self.coast = coast

# Tide data
class TideData(EmbeddedDocument):
    time = StringField(max_length=10)
    height = FloatField()

    def __init__(self, time, height, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time = time
        self.height = height

# Primary key of Tides collection
class TidesKey(EmbeddedDocument):
    aac = StringField(max_length=10)
    date = LongField() # ordinal

    def __init__(self, aac, date, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aac = aac
        self.date = date

# Tides collection
class Tides(Document):
    id = EmbeddedDocumentField(TidesKey, primary_key=True)
    name = StringField(max_length=50)
    tide_data = ListField(EmbeddedDocumentField(TideData))

    def __init__(self, id, name, tide_data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = id
        self.name = name
        self.tide_data = tide_data

# Import data to BoatRamps collection
def import_boat_ramps():
    CONN = connect('comp9321_ass3', host='mongodb://deanna:deanna@ds123770.mlab.com:23770/comp9321_ass3',
                   username='deanna', password='deanna')
    with open('../data/boat_ramp_data_nsw.geojson', 'r') as f:
        boat_ramps = json.loads(f.read())
    sites_dict = get_sites()
    ranges = coast_ranges()
    for br in boat_ramps['features']:
        properties = br['properties']
        br_id = properties['cartodb_id']
        br_coordinates = br['geometry']['coordinates']
        br_properties = BoatRampProperties(br_id, properties['boat_ramp_name'], properties['suburb'], properties['street'],
                                           properties['postcode'], properties['asset_owner'], properties['contact_number'],
                                           properties['waterway_name'], properties['waterway_access'], properties['car_spaces'],
                                           properties['number_ramp_lanes'], properties['ramp_condition'], properties['ramp_material'],
                                           sites_dict[br_id]['is_near_ocean'], properties['has_bbq'], properties['has_bins'],
                                           properties['has_fee_payable'], properties['has_fish_cleaning_table'], properties['has_fuel'],
                                           properties['has_kiosk'], properties['has_lighting'], properties['has_pontoon_nearby'],
                                           properties['has_pontoon_ramp'], properties['has_toilets'])
        tide = sites_dict[br_id]['tide']
        br_tide = TidePredictionSite(tide['aac'], tide['coordinates'], tide['name'], tide['distance'])
        waverider = sites_dict[br_id]['waverider']
        ## If importing BoatRampsSmall
        # if waverider['distance'] > 20 or tide['distance'] > 3:
        #     continue
        br_waverider = WaveriderBuoy(waverider['id'], waverider['coordinates'], waverider['name'], waverider['distance'])
        BoatRamps(br_id, br_coordinates, br_properties, br_tide, br_waverider,
                  get_coast_name(br_coordinates, ranges) if sites_dict[br_id]['is_near_ocean'] else 'Not coastal').save()
    CONN.close()

# Import data to Tides collection
def import_tides():
    if not os.path.exists('pdf_doc'):
        download_pdf()
    month_dict = {'JANUARY': 1, 'FEBRUARY': 2, 'MARCH': 3, 'APRIL': 4, 'MAY': 5, 'JUNE': 6,
             'JULY': 7, 'AUGUST': 8, 'SEPTEMBER': 9, 'OCTOBER': 10, 'NOVEMBER': 11, 'DECEMBER': 12}
    CONN = connect('comp9321_ass3', host='mongodb://deanna:deanna@ds123770.mlab.com:23770/comp9321_ass3',
                   username='deanna', password='deanna')
    for file in os.listdir('pdf_doc'):
        location = file.split('.')[0]
        data = get_pdf_data(f'pdf_doc/{file}')
        aac = link_location_mapping[location][0]
        name = link_location_mapping[location][1]
        for month in data.keys():
            for day in data[month]:
                id = TidesKey(aac, date(2018, month_dict[month], day['date'][0]).toordinal())
                tide_data = []
                for d in day['tide_data']:
                    hour = int(d[0][0:2])
                    minute = int(d[0][2:])
                    tide_data.append(TideData(time(hour, minute).strftime('%I:%M %p').strip('0'), d[1]))
                Tides(id, name, tide_data).save()
    CONN.close()

if __name__ == '__main__':
    pass
    #import_boat_ramps()