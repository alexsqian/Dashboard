google.charts.load('current', {packages: ['corechart']});
    google.charts.setOnLoadCallback(drawChart);

    filesdata = {% autoescape off %}{{ files }}{% endautoescape %}

    function drawChart() {

      var data = new google.visualization.DataTable(filesdata);

      var options = {
        title: 'Files Data',
        width: 900,
        height: 500,
        focusTarget: 'category',
        haxis: {
          format: 'none'
        }

      };

      var chart = new google.visualization.LineChart(document.getElementById('mychart'));
      chart.draw(data, options)
    };




 google.charts.load('current', {packages: ['corechart']});
    google.charts.setOnLoadCallback(drawChart);

    filesdata = {% autoescape off %}{{ files }}{% endautoescape %}
    drivedata = {% autoescape off %}{{ drive }}{% endautoescape %}
    uploaderdata = {% autoescape off %}{{ uploader }}{% endautoescape %}
    faspexdata = {% autoescape off %}{{ faspex }}{% endautoescape %}

    function drawChart(appName, data) {

      var files = new google.visualization.DataTable(filesdata);
      var drive = new google.visualization.DataTable(drivedata);

      var options = {
        title: 'Files Data',
        width: 900,
        height: 500,
        focusTarget: 'category',
        haxis: {
        }
      };


      var fileschart = new google.visualization.LineChart(document.getElementById('fileschart'));
      fileschart.draw(files, options)

      var drivechart = new google.visualization.LineChart(document.getElementById('drivechart'));
      drivechart.draw(drive, options)
    };



      <table class="columns">
    <tr>
      <td><div id="fileschart" style = "border: 1px solid #ccc"></div></td>
      <td><div id="drivechart" style = "border: 1px solid #ccc"></div></td>
    </tr>
  </table>




google.charts.load('current', {packages: ['corechart']});
    google.charts.setOnLoadCallback(drawDashboard);

    // filesdata = {% autoescape off %}{{ files }}{% endautoescape %}
    // drivedata = {% autoescape off %}{{ drive }}{% endautoescape %}
    // uploaderdata = {% autoescape off %}{{ uploader }}{% endautoescape %}
    // faspexdata = {% autoescape off %}{{ faspex }}{% endautoescape %}

    function drawChart(appName, data) {

      var container = document.getElementById("container");

      // TODO: check if container contains a div with id = "drivechart"
      // If NO, create the <div> with javascript, insert it into #container
      
      // Insert data into #container > #drivechart

      var dashboard = new google.visualization.Dashboard(
          document.getElementById('programmatic_dashboard_div'));

      var dateRangeslider = new google.visualization.ControlWrapper({
        'containerId': 'programmatic_control_div',
        'controlType': 'ChartRangeFilter'
        'options': {
          'filterColumnIndex': 0,
          'ui' {
            'chartType': 'LineChart',
            'snapToData': true

          }
        }

      });

      var files = new google.visualization.DataTable(filesdata);
      var drive = new google.visualization.DataTable(drivedata);

      var options = {
        title: 'Files Data',
        width: 900,
        height: 500,
        focusTarget: 'category',
        haxis: {
        }
      };


      var fileschart = new google.visualization.LineChart(document.getElementById('fileschart'));
      fileschart.draw(files, options)

      var drivechart = new google.visualization.LineChart(document.getElementById('drivechart'));
      drivechart.draw(drive, options)
    };