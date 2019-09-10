////// Create bubble chart:
var width = 800,
    height = 800;

// create svg to hold chart
var svg = d3.select("#bubble-chart")
    .append("svg")
    .attr("class", "chart")
    .attr("height", height)
    .attr("width", width)


// grab user data to be used when chart is created
d3.queue()
    .defer(d3.json, "/bubble-chart-data")
    .await(ready)


function ready (error, datapoints) {
    
    // create scale for circle sizes
    let minData = d3.min(datapoints, (d) => d.units );
    let maxData = d3.max(datapoints, (d) => d.units );
    let sizeScale = d3.scaleLinear()
        .domain([minData, maxData])
        .range([32, 70]);

    // create groups to contain cirlces + labels
    var groups = svg.selectAll("g")
        .data(datapoints)
        .enter()
        .append("g")
        .attr("class", "circle-group")
        .attr("assoc", function (d) {
            return d.associations;
        });

    // add circles to groups
    var circles = groups.append("circle")
        .attr("r", (d) => sizeScale(d.units))
        .attr("fill", function (d) {
            return d.fill;
        });

    // add labels to groups
    var labels = groups.append("text")
        .text((d) => d.label)
        .attr("text-anchor", "middle");

    // this will prevent circles from overlapping, w/ padding
    var collideForce = d3.forceCollide(function(d) {
        return sizeScale(d.units) + 3;
    });

    // create force to move circles to center of svg
    var simulation = d3.forceSimulation()
        .force("x", d3.forceX(width / 2).strength(0.05))
        .force("y", d3.forceY(height / 2).strength(0.05))
        .force("collide", collideForce);

    // move circles to center of svg
    function moveCircles () {
        groups
            .attr("transform", function (d) {
                return `translate(${d.x},${d.y})`;
            });
    }

    simulation.nodes(datapoints)
        .on("tick", moveCircles);

    // create forces to cluster circles by group
    var splitForceX = d3.forceX(function(d) {

        if (d.group === 0) {
            return width * 1/2;
        } else if (d.group === 1) {
            return width * 1/3;
        } else if (d.group === 2) {
            return width * 2/3;
        } else if (d.group === 3) {
            return width * 1/4;
        } else if (d.group === 4) {
            return width * 3/4;
        } 
    });

    var splitForceY = d3.forceY(function(d) {

        if (d.group === 0) {
            return height * 1/4;
        } else if (d.group === 1) {
            return height * 2/3;
        } else if (d.group === 2) {
            return height * 2/3;
        } else if (d.group === 3) {
            return height * 1/2;
        } else if (d.group === 4) {
            return height * 1/2;
        } 
    });

    // this will re-up energy & move circles to new locations
    function groupCircles () {
        simulation.nodes(datapoints)
            .force("x", splitForceX)
            .force("y", splitForceY)
            .alphaTarget(0.5)
            .restart();
    }

    // when "group" button is clicked, group circles by event type
    d3.select("#group").on("click", function () {
        groups.datum(function(d) {
            if (d.type === "habit") {
                d.group = 0;           
            } else if (d.type === "influence") {
                d.group = 1;
            } else if (d.type === "symptom") {
                d.group = 2;
            }

            return d;
        });

        groupCircles();
    });

    // create forces to move circles back to center
    var combineForceX = d3.forceX(width / 2).strength(0.06);
    var combineForceY = d3.forceY(height / 2).strength(0.06);

    // this will re-up energy & move circles back to center
    d3.select("#ungroup").on("click", function () {
        simulation.nodes(datapoints)
            .force("x", combineForceX)
            .force("y", combineForceY)
            .alphaTarget(0.5)
            .restart();
    });

    // when any circle is clicked, cluster by circles associated
    // vs not associated  with that circle
    d3.selectAll("#bubble-chart .circle-group").on("click", function (d) {
        
        clickedCircle = d3.select(this);
        associations = clickedCircle.attr("assoc");

        // update group to reflect association or not
        groups.datum(function(d) {
            if (associations.includes(d.label)) {
                d.group = 3;           
            } else {
                d.group = 4;
            }

            return d;
        });

        // make sure clicked circle in associated group, too
        clickedCircle.datum(function (d) {
            d.group = 3;
            return d;
        });
        
        groupCircles();
    });

}