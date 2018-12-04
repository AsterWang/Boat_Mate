// Author: Pengyan Rao, z5099703 (function: create_weather_div)
// to create weather div

// document.addEventListener('DOMContentLoaded', () => {

function create_weather_div(lat, lon) {

    // Initialize new request
    const request = new XMLHttpRequest();
    // const currency = document.querySelector('#weather_div').value;
    request.open('GET', `http://127.0.0.1:5000/weather?lat=${lat}&lon=${lon}`);

    // Callback function for when request completes
    request.onload = () => {
        // Extract JSON data from request
        const data = JSON.parse(request.responseText);

        // Update the result div
        if (data.success == "success") {
            document.querySelector('#result_weather').innerHTML = parse_weather_json(data);
            forecast_graph(data);
        }
        else {
            document.querySelector('#result_weather').innerHTML = 'There was an error.';
        }
    }
    console.log(`weather.js: ${lat}, ${lon}`);

    // Send request
    request.send();
    return false;
};

function forecast_graph(data) {
    var forecast = data['forecast']
    var forecast_length = forecast.length
    var labels_date = []
    var high_temp = []
    var low_temp = []
    for (i=0; i < forecast_length - 1; i++) {
      var day_record = forecast[i];
      date = day_record['date'].slice(5,);
      labels_date.push(date)
      weather = day_record['weather'][0]
      temp_max = Math.round(day_record['temp_max']-273) + 2
      temp_min = Math.round(day_record['temp_min']-273) - 1
      high_temp.push(temp_max)
      low_temp.push(temp_min)
      icon = day_record['icon']
      // console.log(date,temp_max,temp_min,weather)
    };

    var ctx = document.getElementById("myChart");
    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels_date,
            datasets: [
            {
    						label: 'Min Temperature',
                data: low_temp,
                backgroundColor: 'rgba(255, 99, 132, 1)',
                borderColor: 'rgba(255, 99, 132, 0.3)',
                borderWidth: 2,
                pointRadius: 7,
                fill: false
            },
            {
                label: 'Max Temperate',
                data: high_temp,
                backgroundColor: 'rgba(54, 162, 235, 1)',
                borderColor: 'rgba(54, 162, 235, 0.3)',
                borderWidth: 2,
                pointRadius: 7,
                fill: false
            },
            ]
        },
        options: {
        	  title: {
            		text: 'Next Five Days Forecast',
                display: true,
            },
    		    tooltips: {
              mode: 'index',
              intersect: false
            },
            hover: {
    					mode: 'nearest',
    					intersect: true
    				},
            responsive: true,
            scales: {
    					xAxes: [{
    						display: true,
    						scaleLabel: {
    							display: true,
    						}
    					}],
    					yAxes: [{
    						display: true,
    						scaleLabel: {
    							display: true,
    						}
    					}]
    				}
        }
    });
};

function parse_weather_json(data) {
    // create html here
    // console.log(JSON.stringify(data['today_weather']))
    var condition = data['today_weather']['condition']
    var description = data['today_weather']['description']
    var temp = data['today_weather']['temp']
    var max_temp = Math.round(data['today_weather']['temp_max']-273)+3
    var min_temp = Math.round(data['today_weather']['temp_min']-273)-2
    var humidity = data['today_weather']['humidity']
    var pressure = data['today_weather']['pressure']
    var icon = data['today_weather']['icon']
    var uvi = data['uvi']
    var forecast = data['forecast']
    var forecast_length = forecast.length
    // console.log(forecast)

    let html_text =
        "<h3>Weather</h3>" +
        "<dl>" +
            "<dt><font size=25>" + min_temp + "~" + max_temp + "°c</font>" + "    <img src='http://openweathermap.org/img/w/" + icon +".png' style=\"width:120px;height:120px;\">" +"</dt>"

    if (uvi < 2.9) {
      uvi = String(data['uvi']) + " (Low)";
    } else if (3.0 < uvi < 5.9) {
      uvi = String(data['uvi']) + " (Moderate)";
    } else if (6.0 < uvi < 7.9) {
      uvi = String(data['uvi']) + " (High)";
    } else if (8.0 < uvi < 10.9) {
      uvi = String(data['uvi']) + " (Very high)";
    } else {
      uvi = String(data['uvi']) + " (Extreme)";
    }
    console.log(icon)

    html_text +=
            "<dt>Pressure: "+ pressure + "hPa</dt>" +
            "<dt>Humidity: "+ humidity + "%</dt>" +
            "<dt>UV: "+ uvi + "</dt>" +
          "</dl>";
    return html_text
};
