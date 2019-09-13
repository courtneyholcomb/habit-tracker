let eventInputTrack = $("#event-type-track");


// this will populate the dropdown menus based on user's tracked event types
// if user has nothing added for that type, link to add new page
function changeForm () {
    
    let type = eventInputTrack.val();

    if (type == "habit") {

        if ($("#habit-id").text().trim() != "") {
            
            $("#habit-id").attr("hidden", false);
            $("#habit-id").attr("required", true);
            $("#change-type1").text("Habit");
            $("#change-num").text("Units");

            $("#influence-id").attr("hidden", true);
            $("#symptom-id").attr("hidden", true);

        } else {
            
            $("#type-dependent").attr("hidden", true);
            $("#change-type2").text("habits");
            $("#new-prompt").attr("hidden", false);
        }

    } else if (type == "influence") {

        if ($("#influence-id").text().trim() != "") {

            $("#influence-id").attr("hidden", false);
            $("#influence-id").attr("required", true);
            $("#change-type1").text("Influence");
            $("#change-num").text("Intensity");

            $("#habit-id").attr("hidden", true);
            $("#symptom-id").attr("hidden", true);

        } else {
            
            $("#type-dependent").attr("hidden", true);
            $("#change-type2").text("influences");
            $("#new-prompt").attr("hidden", false);
        }

    } else if (type == "symptom") {

        if ($("#symptom-id").text().trim() != "") {

            $("#symptom-id").attr("hidden", false);
            $("#symptom-id").attr("required", true);
            $("#change-type1").text("Symptom");
            $("#change-num").text("Intensity");

            $("#influence-id").attr("hidden", true);
            $("#habit-id").attr("hidden", true);

        } else {

            $("#type-dependent").attr("hidden", true);
            $("#change-type2").text("symptoms");
            $("#new-prompt").attr("hidden", false);
        }
    }
}


// update form when page loads, when user chooses new event type, when user submits new form
$(window).on("load", changeForm);
eventInputTrack.on("change", changeForm);
$("#new-form").on('submit', changeForm)

// get location when button is clicked
$("#location-button").on('click', getLocation);

// track event when user submits form
$("#track-form").on('submit', trackEvent);


// this will get the user's location from the browser
function getLocation(event) {
    event.preventDefault();

    navigator.geolocation.getCurrentPosition(function (position) {
            $("#location").val(`${position.coords.latitude},${position.coords.longitude}`);
    });

    alert("Location retrieved");
}


// this will track event based on user inputs
function trackEvent(event) {

    event.preventDefault();

    const inputs = { 
        eventType: eventInputTrack.val(), 
        typeId: $(".type-id:visible").val(),
        num: $("#num").val(),
        datetime: $("#datetime").val(), 
        location: $("#location").val()
    };

    $.post("/track", inputs, function (response) {
        if (response.includes("tracked successfully")) {
            alert(response);

            $("#track-form")[0].reset();
            changeForm();
        }
    });
}


// this will enable GCal and track events from selected time period
// (or trailing week by default)
function trackGcalHabits(event) {
    event.preventDefault();
    
    const inputs = { 
        startDate: $("#gcal-start-date").val(),
        endDate: $("#gcal-end-date").val()
    };
    
    $.post("/track-gcal-habits", inputs, function (response) {
        if (response == "") {
            alert("No new events to track.");
        } else {
            alert(`Events Tracked:\n${response}`);
        }
    });
}

// track GCal events when user clicks button 
$("#gcal-habits-button").on('click', trackGcalHabits);
