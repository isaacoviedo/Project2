function DisplayChartOnButtonClick() {
    //get dates entered by the user in html form
    var graphStartDate = document.getElementById('GraphStartDate').value;
    var graphEndDate = document.getElementById('GraphEndDate').value;
    var predictDay = document.getElementById('predictDay').value;

    // Load the Visualization API and the corechart package.
    google.charts.load('current', {'packages':['corechart']});

    // Set a callback to run when the Google Visualization API is loaded.
    google.charts.setOnLoadCallback(drawCharts);


    function drawCharts() {
        if(graphStartDate && graphEndDate)
            refreshOldChart();

        if(predictDay)
            refreshPredictiveChart();
    }

    function refreshOldChart(){
        drawOldChart();
        setTimeout(function () {
        refresh();
        }, 60000); // 60000 is a minute (60000 ms)
    }

    function refreshPredictiveChart(){
        drawPredictiveChart();
        setTimeout(function () {
        refresh();
        }, 60000); // 60000 is a minute (60000 ms)
    }   

     // Callback that creates and populates a data table,
     // instantiates the chart, passes in the data and
     // draws it.
     function drawOldChart() {
         
         // AJAX request to get data between user input of dates
         $.ajax({
             type: "POST",
             url: "../PHP/GetTimeStampCountJsonData.php",
             data: {"GraphStartDate": graphStartDate, "GraphEndDate": graphEndDate},
             dataType: "JSON",
             cache: false,
             success: function (response) {
                 console.log(response);
                 // Create our data table out of JSON data loaded from server.
                 var data = new google.visualization.DataTable();
                 data.addColumn('string', 'Time Stamp');
                 data.addColumn('number', 'Number of cars');
                 for(var key in response) {
                     data.addRow([ key, Number(response[key]) ]);
                 }

                 // Instantiate and draw our chart, passing in some options.
                 var chart = new google.visualization.LineChart(document.getElementById('Chart1Area'));
                 chart.draw(data, {width: 650, height: 500});
             }
         });
     };
    }

    function drawPredictiveChart() {}
         $.ajax({
             type: "POST",
             url: "../PHP/TrafficModel.php",
             data: {"predictDay": predictDay},
             dataType: "JSON",
             cache: false,
             success: function (response) {
                 console.log(response);
                 // Create our data table out of JSON data loaded from server.
                 var data = new google.visualization.DataTable();
                 data.addColumn('string', 'Hour');
                 data.addColumn('number', 'Number of cars');
                 for(var key in response) {
                    data.addRow([key, Number(response[key])]);
                 }

                 var chart = new google.visualization.ColumnChart(document.getElementById('Chart2Area'));
                 chart.draw(data, {width: 650, height: 500});
             }
         });
     };
}