// Helper Functions
function isFilled(field, val='', isFloat=false) {
    if (isFloat) {
        return parseFloat(field.value) != parseFloat(val);
    }
    return field.value != val && field.value != ''
}

function isChecked(checkbox) {
    return checkbox.checked
}

disabledColor = "rgb(0,0,0,0.2)";

// Input elements
preferencesForm = document.getElementById('preferencesForm')
numClassesInput = document.getElementById('inputNumClasses');
daysCheckButtons = document.getElementsByClassName('btn-check');
distanceInput = document.getElementById('inputDistance');
probabilityInput = document.getElementById('inputProbability');
probabilityRange = document.getElementById('inputProbabilityRange');
earliestTimeInput = document.getElementById('inputEarliestTime');
latestTimeInput = document.getElementById('inputLatestTime');
minBreakInput = document.getElementById('inputMinBreak');
minBreakUnitInput = document.getElementById('inputMinBreakUnit');
maxBreakInput = document.getElementById('inputMaxBreak');
maxBreakUnitInput = document.getElementById('inputMaxBreakUnit');
saveChangesButton = document.getElementById('saveChanges');

// Obtain initial values
initialNumClasses = numClassesInput.value;
initialdaysCheck = {};
for (let checkButton of daysCheckButtons) {
    initialdaysCheck[checkButton.value] = checkButton.checked;
}
initialDistance = distanceInput.value;
initialProbability = probabilityInput.value;
initialEarliestTime = earliestTimeInput.value;
initialLatestTime = latestTimeInput.value;
initialMinBreak = minBreakInput.value;
initialMinBreakUnit = minBreakUnitInput.value;
initialMaxBreak = maxBreakInput.value;
initialMaxBreakUnit = maxBreakUnitInput.value

function checkChangesInForm() {
    /* console.log((() => {
        for (let checkButton of daysCheckButtons) {
            if (initialdaysCheck[checkButton.value] != checkButton.checked) {
                return false;
            }
        }
        return true;
    })());
    console.log(initialNumClasses == numClassesInput.value);
    console.log(initialDistance == distanceInput.value);
    console.log(initialProbability == probabilityInput.value);
    console.log(initialEarliestTime == earliestTimeInput.value);
    console.log(initialLatestTime == latestTimeInput.value);
    console.log(initialMinBreak == minBreakInput.value);
    console.log(initialMinBreakUnit == minBreakUnitInput.value);
    console.log(initialMaxBreak == maxBreakInput.value);
    console.log(initialMaxBreakUnit == maxBreakUnitInput.value); */
    preferencesButtons = document.getElementById('preferencesButtons');
    if (
        initialNumClasses == numClassesInput.value &&
        (() => {
            for (let checkButton of daysCheckButtons) {
                if (initialdaysCheck[checkButton.value] != checkButton.checked) {
                    return false;
                }
            }
            return true;
        })() &&
        initialDistance == distanceInput.value &&
        initialProbability == probabilityInput.value &&
        initialEarliestTime == earliestTimeInput.value &&
        initialLatestTime == latestTimeInput.value &&
        initialMinBreak == minBreakInput.value &&
        initialMinBreakUnit == minBreakUnitInput.value &&
        initialMaxBreak == maxBreakInput.value &&
        initialMaxBreakUnit == maxBreakUnitInput.value
    ){
        console.log("no changes");
        saveChangesButton.disabled = true;
        [].slice.call(preferencesButtons.children).pop();
        document.getElementById("saveChangesPopover").appendChild(saveChangesButton);
    }
    else {
        console.log("changed!");
        saveChangesButton.disabled = false;
        // console.log(document.getElementById("saveChangesPopover").children);
        [].slice.call(document.getElementById("saveChangesPopover").children).pop();
        preferencesButtons.appendChild(saveChangesButton);
    }
}

preferencesForm.addEventListener('change', checkChangesInForm);

//  Output circle IDs
circleIds = {
    'numClasses' : 1,
    'classDays' : 2,
    'distance' : 3,
    'probability' : 4,
    'classTimes' : 5,
    'breakDuration' : 6,
};

// Initialize disabled circles
document.addEventListener("DOMContentLoaded", function() {
    circleIcons = document.getElementsByClassName("disabled");
    for (let icon of circleIcons) {
        icon.classList.add('disabled');
    }
})

probabilityRange.addEventListener('change', function(){
    probabilityInput.value = probabilityRange.value;
});

probabilityInput.addEventListener('change', function(){
    probabilityRange.value = probabilityInput.value;
});

function checkNumClasses() {
    if (isFilled(numClassesInput, "0")) {
        document.getElementById('i-' + circleIds['numClasses'].toString()).classList.remove('disabled');
    }
    else {
        document.getElementById('i-' + circleIds['numClasses'].toString()).classList.add('disabled');
    }
}

numClassesInput.addEventListener('change', checkNumClasses);

var numChecked = 0;

function checkClassDays() {
    /* if (!isChecked(checkButton)) {
        numChecked--;
    }
    else {
        numChecked++;
    }
 */
    if (numChecked == 0) {
        document.getElementById('i-' + circleIds['classDays'].toString()).classList.add('disabled');
    }
    else {
        document.getElementById('i-' + circleIds['classDays'].toString()).classList.remove('disabled');
    }
}

for (let checkButton of daysCheckButtons) {
    checkButton.addEventListener('change', function() {
        if (!isChecked(checkButton)) {
            numChecked--;
        }
        else {
            numChecked++;
        }
        checkClassDays();
    })   
};

function checkDistance() {
    if (isFilled(distanceInput, "0")) {
        document.getElementById('i-' + circleIds['distance'].toString()).classList.remove('disabled');
    }
    else {
        document.getElementById('i-' + circleIds['distance'].toString()).classList.add('disabled');
    }
}

distanceInput.addEventListener('change', checkDistance);

function checkProbabilityInput() {
    if (isFilled(probabilityInput, "0", true)) {
        document.getElementById('i-' + circleIds['probability'].toString()).classList.remove('disabled');
    }
    else {
        document.getElementById('i-' + circleIds['probability'].toString()).classList.add('disabled');
    }
}

probabilityInput.addEventListener('change', checkProbabilityInput);

function checkProbabilityRange() {
    if (isFilled(probabilityRange, "0", true)) {
        document.getElementById('i-' + circleIds['probability'].toString()).classList.remove('disabled');
    }
    else {
        document.getElementById('i-' + circleIds['probability'].toString()).classList.add('disabled');
    }
}

probabilityRange.addEventListener('change', checkProbabilityRange);

function checkClassTime() {
    if (isFilled(earliestTimeInput) && isFilled(latestTimeInput)) {
        document.getElementById('i-' + circleIds['classTimes'].toString()).classList.remove('disabled');
    }
    else {
        document.getElementById('i-' + circleIds['classTimes'].toString()).classList.add('disabled');
    }
}

earliestTimeInput.addEventListener('change', checkClassTime);

latestTimeInput.addEventListener('change', checkClassTime);

function checkBreakDuration() {
    if (isFilled(minBreakInput, "0") && isFilled(minBreakUnitInput) && isFilled(maxBreakInput, "0") && isFilled(maxBreakUnitInput)) {
        document.getElementById('i-' + circleIds['breakDuration'].toString()).classList.remove('disabled');
    }
    else {
        document.getElementById('i-' + circleIds['breakDuration'].toString()).classList.add('disabled');
    }
}

minBreakInput.addEventListener("change", checkBreakDuration);
minBreakUnitInput.addEventListener("change", checkBreakDuration);
maxBreakInput.addEventListener("change", checkBreakDuration);
maxBreakUnitInput.addEventListener("change", checkBreakDuration);

function resetNumClasses() {
    numClassesInput.value = 0;
    checkNumClasses();
}

function resetClassDays() {
    for (let checkButton of daysCheckButtons) {
        checkButton.checked = false;
    }
    numChecked = 0;
    checkClassDays();
}

function resetDistance() {
    distanceInput.value = 0;
    checkDistance();
}

function resetProbability() {
    probabilityInput.value = 0;
    probabilityRange.value = 0;
    checkProbabilityInput();
    checkProbabilityRange();
}

function resetClassTimes() {
    earliestTimeInput.value = "";
    latestTimeInput.value = "";
    checkClassTime();
}

function resetBreakDuration() {
    minBreakInput.value = 0;
    minBreakUnitInput.value = "";
    maxBreakInput.value = 0;
    maxBreakUnitInput.value = "";
    checkBreakDuration();
}

function resetAll() {
    resetNumClasses();
    resetClassDays();
    resetDistance();
    resetProbability();
    resetClassTimes();
    resetBreakDuration();
    checkChangesInForm();
}

document.addEventListener("DOMContentLoaded", function(){
    checkNumClasses();
    
    for (let checkButton of daysCheckButtons) {
        if (isChecked(checkButton)) {
            numChecked++;
        }
    }
    checkClassDays();

    checkDistance();
    checkClassTime();
    checkBreakDuration();
})


