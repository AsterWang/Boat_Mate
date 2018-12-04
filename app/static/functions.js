let map;
let markers = [];
let filters = {has_bbq:false, has_bins:false,has_fee_payable:false,
              has_fish_cleaning_table:false,has_fuel:false,
              has_kiosk:false,has_lighting:false,has_pontoon_nearby:false,
              has_pontoon_ramp:false,has_toilets:false};

$(function () {
     $("select").multiselect({
        noneSelectedText: "==Filters==",
        checkAllText: "Select All",
        uncheckAllText: 'Cancel All',
        selectedList:4,
    });
    $("#sela").on('change',function () {
        map_filter($(this).val());
        filter_markers()
    });
});

let get_options = function () {
    let option_array = [];
    for (option in filters){
        if(filters[option]){
            option_array.push(option)
        }
    }
    return option_array;
};

let filter_markers = function () {
    let set_filters = get_options();
    for (i = 0; i< markers.length; i++){
        marker = markers[i];
        let visible = true;
        for (opt = 0; opt < set_filters.length; opt++){
            if (!marker.properties[set_filters[opt]]){
                visible = false;
            }
        }
        marker.setVisible(visible);
    }
};

Array.prototype.contains = function (obj) {
    let i = this.length;
    while (i--) {
        if (this[i] === obj) {
            return true;
        }
    }
    return false;
};

let map_filter = function (id_value) {
    let filters_key = Object.keys(filters);
    for (i=0; i < filters_key.length; i++) {
        let index = id_value.contains(filters_key[i]);
        if (index) {
            filters[filters_key[i]] = true
        } else {
            filters[filters_key[i]] = false
        }
    }
};

function load_markers(){
    let infowindow = new google.maps.InfoWindow();
    geojson_url = 'http://127.0.0.1:5000/boatramps/test';
    // geojson_url = 'http://127.0.0.1:5000/boatramps';
    $.getJSON(geojson_url, function(result) {
        // alert("loading markers successfully!");
        data = result['features'];
        $.each(data, function(key, val) {
            let asset_owner = val['properties']['asset_owner'];
            let boat_ramp_name = val['properties']['boat_ramp_name'];
            let contact_number =val['properties']['contact_number'];
            let waterway_name = val['properties']['waterway_name'];
            let access = val['properties']['waterway_access'];
            let car_spaces = val['properties']['car_spaces'];
            let number_ramp_lanes = val['properties']['number_ramp_lanes'];
            let ramp_condition = val['properties']['ramp_condition'];

            const image = {
                url: 'https://developers.google.com/maps/documentation/javascript/examples/full/images/beachflag.png',
                // This marker is 20 pixels wide by 32 pixels high.
                size: new google.maps.Size(20, 32),
                // The origin for this image is (0, 0).
                origin: new google.maps.Point(0, 0),
                // The anchor for this image is the base of the flagpole at (0, 32).
                anchor: new google.maps.Point(0, 32)
            };


            // load marker with coordinates
            let marker = new google.maps.Marker({
                position:{lat:val.geometry.coordinates[1],lng:val.geometry.coordinates[0]},
                title: asset_owner,
                icon:image,
                map: map,
                properties: val['properties'],
            });

            // marker popup windown message
            let markerInfo =
                "<h5>"+boat_ramp_name+"</h5>"+
                "<div style='width:300px; text-align: left;'>"+
                    "<div>" +
                        "<span>Asset Owner: </span>"+
                        "<span id='asset_owner'>"+asset_owner+"</span>"+
                    "</div>"+
                    "<div>" +
                        "<span>Contact Number: </span>"+
                        "<span>"+contact_number+"</span>"+
                    "</div>"+
                    "<div>" +
                        "<span>Waterway: </span>"+
                        "<span>"+waterway_name+"</span>"+
                    "</div>"+
                    "<div>" +
                        "<span>Access: </span>"+
                        "<span>"+access+"</span>"+
                    "</div>"+
                    "<div>" +
                        "<span>Car Space: </span>"+
                        "<span>"+car_spaces+"</span>"+
                    "</div>"+
                    "<div>" +
                        "<span>Number of Ramp Lanes: </span>"+
                        "<span>"+number_ramp_lanes+"</span>"+
                    "</div>"+
                    "<div>" +
                        "<span>Ramp Condition: </span>"+
                        "<span>"+ramp_condition+"</span>"+
                    "</div>"+
                "</div>";


            marker.addListener('click', function() {
                infowindow.setContent(markerInfo);
                infowindow.setPosition(marker.position);
                infowindow.setOptions({pixelOffset: new google.maps.Size(0,-30)});
                infowindow.open(map);
                create_weather_div(val.geometry.coordinates[1],val.geometry.coordinates[0]);
                safety_div(val['properties']['id']);
            });
            markers.push(marker)
        });
    });
}

function initMap() {
    // Create a new StyledMapType object, passing it an array of styles,
    // and the name to be displayed on the map type control.
    var styledMapType = new google.maps.StyledMapType(
      [
        {
          "featureType": "administrative.land_parcel",
          "elementType": "labels",
          "stylers": [
            {
              "visibility": "off"
            }
          ]
        },
        {
          "featureType": "poi",
          "elementType": "labels.text",
          "stylers": [
            {
              "visibility": "off"
            }
          ]
        },
        {
          "featureType": "poi.business",
          "stylers": [
            {
              "visibility": "off"
            }
          ]
        },
        {
          "featureType": "road",
          "stylers": [
            {
              "visibility": "off"
            }
          ]
        },
        {
          "featureType": "road",
          "elementType": "labels.icon",
          "stylers": [
            {
              "visibility": "off"
            }
          ]
        },
        {
          "featureType": "road.local",
          "elementType": "labels",
          "stylers": [
            {
              "visibility": "off"
            }
          ]
        },
        {
          "featureType": "transit",
          "stylers": [
            {
              "visibility": "off"
            }
          ]
        }
      ],



        {name: 'Styled Map'});

    map = new google.maps.Map(document.getElementById('map-canvas'), {
        center: {lat: -25.363, lng:131.044},
        zoom: 4,
        gestureHandling: 'greedy'
    });

    //Associate the styled map with the MapTypeId and set it to display.
    map.mapTypes.set('styled_map', styledMapType);
    map.setMapTypeId('styled_map');

    //set dialog
    // let dialog = document.getElementById('buttons');
    // map.controls[google.maps.ControlPosition.RIGHT_TOP].push(dialog);
    // dialog.index = 2;

    //set search box
    let input = document.getElementById('pac-input');
    map.controls[google.maps.ControlPosition.TOP_CENTER].push(input);
    let searchBox = new google.maps.places.SearchBox((input));
    google.maps.event.addListener(searchBox, 'places_changed', function() {
        searchBox.set('map', null);
        let places = searchBox.getPlaces();
        let bounds = new google.maps.LatLngBounds();
        let i, place;
        for (i = 0; place = places[i]; i++) {
            (function(place) {
                let marker = new google.maps.Marker({

                    position: place.geometry.location
                });
                marker.bindTo('map', searchBox, 'map');
                google.maps.event.addListener(marker, 'map_changed', function() {
                    if (!this.getMap()) {
                        this.unbindAll();
                    }
                });
                bounds.extend(place.geometry.location);


            }(place));

        }
        map.fitBounds(bounds);
        searchBox.set('map', map);
        map.setZoom(Math.min(map.getZoom(),12));

    });

    //set Filters on the top of google map
    let options = document.getElementById("filter_selection");
    options.index = 1;
    map.controls[google.maps.ControlPosition.LEFT_TOP].push(options);

    //loading markers
    load_markers();
}

google.maps.event.addDomListener(window, 'load', initMap);
