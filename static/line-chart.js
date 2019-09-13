////// Create line chart:
let line_canvas = $("#line-chart").get(0).getContext("2d");

// fill in chart info when page loads (default time range is past week)
window.onload = function () {
    $.post("/line-chart-data", function (response) {
        let data = $.parseJSON(response);
        let labels = data.labels;
        let datasets = data.datasets;

        let line_chart = new Chart(line_canvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: datasets
            }

        });
    });
}

// Update chart if date range selected & submitted
$("#update-chart").on('click', function (event) {
    event.preventDefault();

    let dates = {
        startDate: $("#line-start-date").val(),
        endDate: $("#line-end-date").val()
    };

    $.post("/line-chart-data", dates, function (response) {
        let data = $.parseJSON(response);
        let labels = data.labels;
        let datasets = data.datasets;

        let line_chart = new Chart(line_canvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: datasets
            }

        });
    });
});