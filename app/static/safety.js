// Author: Chenxuan Rong, z5121987 (function: fetch safety info)
// to add into safety sector

function safety_div(boatrampid) {

    // Initialize new request
    const request = new XMLHttpRequest();
    // const currency = document.querySelector('#weather_div').value;
    url_link = `http://127.0.0.1:5000/boatramps/safetyanalysis/` + String(boatrampid)
    request.open('GET', url_link);

    // Callback function for when request completes
    request.onload = () => {
        // Extract JSON data from request
        const data = JSON.parse(request.responseText);

        var safety_score = data['safety_score']
        var sea_temp = data['waverider']['data']['sea_temp']['data']
        var sea_temp_info = data['waverider']['data']['sea_temp']['info']
        var wave_height = data['waverider']['data']['wave_height']['data']
        var wave_height_info = data['waverider']['data']['wave_height']['info']
        var wind = data['wind']

        let safety_html_text = "<h3>Safety Level: "+safety_score +"/10</h3><dl>" + "<dt>Tide</dt>"
        var tide_records = data['tide']['data']
        var tide_records_length = tide_records.length;

        for (var i = 0; i < tide_records_length; i++) {
          console.log(tide_records[i])
          safety_html_text += "<dd>"+tide_records[i]['time']+" ~ "+tide_records[i]['height']+"m</dd>";
        }

        safety_html_text += "<dt>Sea Temperature</dt>"+"<dd>"+sea_temp+"°c ("+ sea_temp_info +")</dd>";
        safety_html_text += "<dt>Wave Height<dt>"+"<dd>"+wave_height+"m ("+wave_height_info+")</dd>"
        safety_html_text += "</dl"


        document.querySelector('#result_score').innerHTML = safety_html_text;

        var warning = data['warning']
        console.log(warning)

        if (jQuery.isEmptyObject(warning)) {
          console.log('empty warning record')
          let warning_html_text = `
              <h3>Warning</h3>
                `;
          document.querySelector('#result_warning').innerHTML = warning_html_text;
        } else {
          let warning_html_text = "<h3>Warning</h3>" + "<ul>"

          for (x in warning) {
            var each_warning = warning[x]
            for (record in each_warning) {
              warning_html_text += "<li>" + record +': ' + each_warning[record] + "</li>";
            }
          }
          warning_html_text += "</ul>"
          document.querySelector('#result_warning').innerHTML = warning_html_text;
        }
    }
    console.log(`boat ramp id: ${boatrampid}`);

    // Send request
    request.send();
    return false;
};
