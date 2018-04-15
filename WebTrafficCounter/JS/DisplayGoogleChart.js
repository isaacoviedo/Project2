function DisplayChartOnButtonClick() {
    //get dates entered by the user in html form
    var graphStartDate = document.getElementById('GraphStartDate').value;
    var graphEndDate = document.getElementById('GraphEndDate').value;

    // date inputs cannot be null
    if( graphStartDate && graphEndDate) {

         // Load the Visualization API and the corechart package.
         google.charts.load('current', {'packages':['corechart']});

         // Set a callback to run when the Google Visualization API is loaded.
         google.charts.setOnLoadCallback(drawChart);

         // Callback that creates and populates a data table,
         // instantiates the pie chart, passes in the data and
         // draws it.
         function drawChart() {
             
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
                     data.addColumn('number', 'Number of students');
                     for(var key in response) {
                         data.addRow([ key, Number(response[key]) ]);
                     }

                     // Instantiate and draw our chart, passing in some options.
                     var chart = new google.visualization.LineChart(document.getElementById('ChartArea'));
                     chart.draw(data, {width: 650, height: 500});
                 }
             });
         };
    }
    else {
        //alert user if user attempts to graph without entering dates
         alert("Please choose start and end date to display graph");
    }
}