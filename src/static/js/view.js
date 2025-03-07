// https://stackoverflow.com/questions/74396736/the-requested-module-does-not-provide-an-export-named-default
import html2canvas from "./html2canvas.js";

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