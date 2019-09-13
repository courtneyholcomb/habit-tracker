// this will get the user's location from the browser
function getLocation(event) {
    event.preventDefault();
    navigator.geolocation.getCurrentPosition(function (position) {
            $("#location").val(`${position.coords.latitude},${position.coords.longitude}`);
        });
    alert("Location retrieved");
}

// get location when button is clicked
$("#location-button").on('click', getLocation);


function getClasses() {

    $("#yoga-classes").html("Searching for best classes...");

    let formData = {
        dateInput: $("#date-input").val(),
        start: $("#start").val(),
        end: $("#end").val(),
        location: $("#location").val()
    };

    $.get("/yoga-classes", formData, function (response) {
        let data = $.parseJSON(response);
        let classes = `<table id="class-table" class="table .table-sm table-bordered"><thead><tr><th>Studio</th>
            <th>Instructor</th><th>Class Title</th><th>Start</th>
            <th>Duration</th><th>Transit</th><th>Biking</th></tr></thead><tbody>`;

        for (let clas of data) {
            classes += `<tr><td>${clas.studio}</td><td>${clas.instructor}</td>
                <td>${clas.title}</td><td>${clas.start}</td>
                <td>${clas.duration} min</td><td>${clas.transit}</td>
                <td>${clas.biking}</td></tr>`;  
        }
        classes += `</tbody></table>`;

        $("#yoga-classes").html(classes);
        
        $("#submit-button").attr("disabled", false);

        $('#class-table').DataTable({
            paging: false
        });
    });
}

window.onload = getClasses();
$("#submit-button").on("click", function (event) {
    event.preventDefault();

    $("#submit-button").attr("disabled", true);

    getClasses();


});
