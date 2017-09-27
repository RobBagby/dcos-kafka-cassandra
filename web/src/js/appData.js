function plotData(url) {
        function updateData() {
      d = new Date();
      now = d.getTime()
            $.ajax({url: url,
            contentType:"application/json; charset=utf-8",
            success: function(result){
              var viewData = JSON.parse(result)
              $("#queue_length").text(viewData.latest_lag);
              writeLastAlerts(viewData.last_alerts.alerts);
              
              setTimeout(function() {
              plotData();
              }, 1000);
            },
            error: function (request, status, error) {
              // Ignore REST API errors, the orchestrartor will bring it back up in time		    
              setTimeout(function() {
              plotData();
              }, 1000);
            }
            });
        }

        updateData();
    }

    function writeLastAlerts(alerts){
      var table = $('<div></div>').addClass('table');
      var row = $('<div></div>').addClass('row').addClass('header');
      row.append($('<div></div>').addClass('cell').text('Time'));
      row.append($('<div></div>').addClass('cell').text('Id'));
      row.append($('<div></div>').addClass('cell').text('Temp'));
      table.append(row);

      for (var i = 0, len = alerts.length; i < len; i++) {
        var row = $('<div></div>').addClass('row');
        row.append($('<div></div>').addClass('cell').text(alerts[i].event_date.split(' ')[1]));
        row.append($('<div></div>').addClass('cell').text(alerts[i].sensor_id));
        row.append($('<div></div>').addClass('cell').text(alerts[i].temperature));
        
        table.append(row);
      }
      document.getElementById('last_alerts').innerHTML = '';
      $('#last_alerts').empty().append(table);
    }