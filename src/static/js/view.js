// https://stackoverflow.com/questions/74396736/the-requested-module-does-not-provide-an-export-named-default
import html2canvas from "./html2canvas.js";

/* Dynamically adjusts the height of the tiles in the timetable */
function adjustTableHeight(tableID) {
    // Get the timetable associated with `tableID`
    var timetable = document.getElementById(tableID);

    // Get the rows and number of rows
    var timetableChildren = timetable.children[0].children
    var numChildren = timetableChildren.length

    // The header occupies 2% of the table height => 98% for the remaining
    var rowHeight = 98/(numChildren-1);

    // Convert HTML collection into an array
    // https://stackoverflow.com/questions/222841/most-efficient-way-to-convert-an-htmlcollection-to-an-array
    let arr = Array.from(timetableChildren);

    // Set the height of each row
    for (let row of arr) {
        row.style.height = String(rowHeight) + "%";
    }
}

adjustTableHeight("timetable");
adjustTableHeight("exportTimetable");

/* Converts the `div` of id `export-sched` into a canvas */
html2canvas(
    document.getElementById('export-sched')
).then( function(canvas) {

    // Get container of the schedule image
    document.getElementById('export-container').appendChild(canvas);

    // Hide the reference `div`
    document.getElementById('export-sched').style.display = "none";

    // Modify the dimensions of the displayed image
    document.getElementById('export-container').children[0].style.width = "100%";
    document.getElementById('export-container').children[0].style.height = "auto";

    // Configure the download URL of the image
    // https://www.youtube.com/watch?v=qgyCX8IyBZo
    const imageURL = canvas.toDataURL("image/png");
    var anchor = document.createElement("a");
    anchor.setAttribute("href", imageURL);      // URL of the image download
    anchor.setAttribute("download", "apes");    // filename

    // Put the hyperlink inside the button
    document.getElementById("download-btn").appendChild(anchor);

    // The image has been successfully generated -> hide the cover!
    document.getElementById("cover").style.opacity = "0";

    // For animation only!
    // -- Wait 0.5s before "removing" the cover
    setInterval(()=>{document.getElementById("cover").style.display = "None";}, 500); 
});

// For popovers
// Assisted by: GitHub Copilot
// Date: 03/24/2025
// prompt: how do i add a popover to a button
document.addEventListener('DOMContentLoaded', function () {
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});


document.addEventListener('DOMContentLoaded', function() {
    //const overlay = document.getElementById('removeCourseOverlay');
    
    const deleteButtons = document.querySelectorAll('.removeFromSched');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            document.getElementById('removeFromSched-'+button.id).style.display = 'block';
        });
    });

    document.getElementById("removeFromSchedYes").addEventListener("click", function() {
        document.getElementById('removeCourseFromSched').submit();
    });
    
    const noButtons = document.querySelectorAll('.removeFromSchedNo');
    noButtons.forEach(button => {
        button.addEventListener('click', function() {
            document.getElementById('removeFromSched-'+button.id).style.display = 'none';
        });
    });
});