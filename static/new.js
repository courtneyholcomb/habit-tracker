let eventInputNew = $("#event-type-new");

// show lists of event types when page loads
function showEventTypes() {

    const habitTableTop = "<tr><th>Title</th><th>Unit</th></tr>";
    const inflSympTableTop = "<tr><th>Title</th><th>Scale</th></tr>";

    let habitList = "";
    let influenceList = "";
    let symptomList = "";

    $.get("/user-event-types", function (response) {
        data = $.parseJSON(response)

        for (let habit of data.habits) {
            habitList += `<tr><td>${ habit.label }</td>
                          <td>${ habit.unit }</td></tr>`;
        }

        for (let influence of data.influences) {
            influenceList += `<tr><td>${ influence.label }</td>
                              <td>${ influence.scale }</td></tr>`;
        }

        for (let symptom of data.symptoms) {
            symptomList += `<tr><td>${ symptom.label }</td>
                            <td>${ symptom.scale }</td></tr>`;
        }

        if (habitList != false) {
            $("#habit-list").html(`${habitTableTop} + ${habitList}`);
        } else {
            $("#habit-list").html("You are not currently tracking any habits.");
        } 

        if (influenceList != false) {
            $("#influence-list").html(`${inflSympTableTop} + ${influenceList}`);
        } else {
            $("#influence-list").html("You are not currently tracking any influences.");
        } 
        
        if (symptomList != false) {
            $("#symptom-list").html(`${inflSympTableTop} + ${symptomList}`);
        } else {
            $("#symptom-list").html("You are not currently tracking any symptoms.");
        }
    });
}

$(window).on("load", showEventTypes);


// change input form based on event type selected
eventInputNew.on("change", function() {

    if (eventInputNew.val() == "influence" || eventInputNew.val() == "symptom") {
        $("#unit-or-scale").html(`<label> Intensity scale: 0 to 
            <input type="number" name="unit" id="unit" required></label>`);
    } else if (eventInputNew.val() == "habit") {
        $("#unit-or-scale").html(`<label> Unit of measurement: 
            <input type="text" name="unit" id="unit" required></label>`);
    }
  
});


// when form is submitted, add type to db, reset form & refresh lists
function addEventType(event) {
    event.preventDefault();

    formData = {
        eventType: eventInputNew.val(),
        label: $("#label").val(),
        unit: $("#unit").val()
    };

    getEventData = $.post("/new", formData, function (response) {

        let data = $.parseJSON(response);
        let new_id = data.new_id;

        alert(data.success);

        if (data.success.includes("added successfully")) {

            $("#new-form")[0].reset();

            $("#unit-or-scale").html(`<label>Unit of measurement: 
            <input type="text" name="unit" id="unit" required></label>`);

            showEventTypes();
        }

        console.log(new_id);
        // when new type is added, insert it into tracking dropdown list
        // need to get the type id from /new route and insert here. reformat to JSON and parse things needed 
        if (formData["eventType"] == "habit") {

            $("#habit-id").append(`<option value=${new_id}>${formData["label"]}</option>`);

        } else if (formData["eventType"] == "influence") {

            $("#influence-id").append(`<option value=${new_id}>${formData["label"]}</option>`);

        } else if (formData["eventType"] == "symptom") {

            $("#symptom-id").append(`<option value=${new_id}>${formData["label"]}</option>`);

        }
    });
}

$("#new-form").on("submit", addEventType);
