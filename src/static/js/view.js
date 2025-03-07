// https://stackoverflow.com/questions/74396736/the-requested-module-does-not-provide-an-export-named-default
import html2canvas from "./html2canvas.js";


document.getElementById('export-sched').style.display = "block";
html2canvas(
    document.getElementById('export-sched'),
    /* {
        allowTaint: true,
        imageTimeout: 15000,
        logging: true,
        useCORS: true,
        scrollX: -window.scrollX,
        scrollY: -window.scrollY
    } */
).then( function(canvas) {
    document.getElementById('export-container').appendChild(canvas);
    document.getElementById('export-sched').style.display = "none";
    document.getElementById('export-container').children[0].style.width = "100%";
    document.getElementById('export-container').children[0].style.height = "auto";
});

/* document.getElementById("export").addEventListener("click", capture); */