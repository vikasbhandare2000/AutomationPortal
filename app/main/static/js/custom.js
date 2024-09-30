$(document).ready(function(){
pulse();
});

function pulse() {
    $('#heart').animate({
        fontSize: "12px"
    }, 300, function() {
        $('#heart').animate({
            fontSize: "16px"
        }, 300, function() {
            pulse();
        });
    });
};


function alertbox(status_code,message){

    header = $("#alertbox").find('.modal-header');
    header.removeClass('success');
    header.addClass('alert');

    header.find('h3').html('Alert');
    
    if(status_code != 0){
        $('#alert_status_code').html(status_code);
    }else{
        $('#alert_status_code').html('');
    }
    $('#alert_message').html(message);
    $('#alertbox').modal('show');
}

function infobox(status_code,message){

    header = $("#alertbox").find('.modal-header');
    header.removeClass('alert');
    header.addClass('success');

    header.find('h3').html('Success');
    
    if(status_code != 0){
        $('#alert_status_code').html(status_code);
    }else{
        $('#alert_status_code').html('');
    }
    $('#alert_message').html(message);
    $('#alertbox').modal('show');
}

const color_palette  = ['#FF6633', '#FFB399', '#FF33FF', '#FFFF99', '#00B3E6', 
'#E6B333', '#3366E6', '#999966', '#99FF99', '#B34D4D',
'#80B300', '#809900', '#E6B3B3', '#6680B3', '#66991A', 
'#FF99E6', '#CCFF1A', '#FF1A66', '#E6331A', '#33FFCC',
'#66994D', '#B366CC', '#4D8000', '#B33300', '#CC80CC', 
'#66664D', '#991AFF', '#E666FF', '#4DB3FF', '#1AB399',
'#E666B3', '#33991A', '#CC9999', '#B3B31A', '#00E680', 
'#4D8066', '#809980', '#E6FF80', '#1AFF33', '#999933',
'#FF3380', '#CCCC00', '#66E64D', '#4D80CC', '#9900B3', 
'#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF'];


function charting(chartname, labels, values,barvalues){
    var options = {
        indexAxis: 'y',
        scales: {

        }
    };
    var data = {       
            labels: labels,
            datasets: [{
                label: barvalues,
                backgroundColor: '#563d7c',
                borderColor: '#563d7c', 
                borderWidth: 1, 
                data: values
            }],
    };

    var ctx1 = document.getElementById(chartname).getContext('2d');

    var myChart1 = new Chart(ctx1, {
        type: 'bar',
        data: data,
        options: options
    });
};

function charting2(chartname, labels, values,barvalues){
    var options = {
        indexAxis: 'y',
        scales: {

        }
    };
    var data = {       
            labels: labels,
            datasets: [{
                data: values
            }],
    };

    var ctx1 = document.getElementById(chartname).getContext('2d');

    var myChart1 = new Chart(ctx1, {
        type: 'pie',
        data: data,
        options: options
    });
};

function horizontalBarChartOverlapping(chartname, labels,memoryCapacity,memoryAllocated,memoryUsed){
    var ctx = document.getElementById(chartname).getContext('2d');
    var memoryChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Memory Capacity (GB)',
                data: memoryCapacity,
                backgroundColor: '#0d6efddb',
                grouped: false,
                order: 1,
                catagoryPercentage: 0.5,
                barThickness: 40
            }, {
                label: 'Memory Allocated (GB)',
                data:memoryAllocated,  
                backgroundColor: 'orange',
                catagoryPercentage: 0.3,
                barThickness: 30
            }, {
                label: 'Memory Used (GB)',
                data: memoryUsed, 
                backgroundColor: '#dc3545d9',
                catagoryPercentage: 0.3,
                barThickness: 30
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: false
        },
        scales: {
            y: {
                display: true,
               
            },
            yAxes:[{
                barThickness: 6,
                maxBarThickness: 8
            }]
        }
    });
};