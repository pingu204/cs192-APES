/* Dynamically adjusts the height of the tiles in the timetable */
function adjustTableHeight(tableID) {
    console.log(tableID);
    // Get the timetable associated with `tableID`
    var timetable = document.getElementById(tableID);
    timetable.style.height = "100%";
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

const timeTables = document.querySelectorAll('.time_table');
timeTables.forEach(t => {
    adjustTableHeight(t.id);
})

//adjustTableHeight("timetable");

const sectionBlocks = document.querySelectorAll('.result-card');
sectionBlocks.forEach(t => {
    t.addEventListener("mouseover", function() {
        document.getElementById('timetable').style.display = 'none';
        document.getElementById('table-'+t.id).style.display = 'table';
        console.log("opened " + t.id);
        //adjustTableHeight("table-"+t.id);
    });
    t.addEventListener("mouseleave", function(){
        document.getElementById('timetable').style.display = 'table';
        document.getElementById('table-'+t.id).style.display = 'none';
        console.log("closed " + t.id);
        //adjustTableHeight('timetable');
    })

});

const addedBlocks = document.getElementsByClassName('glow');
for (let block of addedBlocks) {
    var styles = getComputedStyle(block);
    block.style.boxShadow = "0 0 50px " + styles.getPropertyValue("background-color").toString();
    console.log("0 0 30px " + styles.getPropertyValue("background-color").toString()); 
}