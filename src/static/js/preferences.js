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
        icon.style.color = disabledColor;
    }
})

probabilityRange.addEventListener('change', function(){
    probabilityInput.value = probabilityRange.value;
});

probabilityInput.addEventListener('change', function(){
    probabilityRange.value = probabilityInput.value;
});

numClassesInput.addEventListener('change', function(){
    if (isFilled(numClassesInput, "0")) {
        document.getElementById('i-' + circleIds['numClasses'].toString()).style.color = '';
    }
    else {
        document.getElementById('i-' + circleIds['numClasses'].toString()).style.color = disabledColor;
    }
});

var numChecked = 0;
for (let checkButton of daysCheckButtons) {
    checkButton.addEventListener('change', function(){
        if (!isChecked(checkButton)) {
            numChecked--;
        }
        else {
            numChecked++;
        }

        if (numChecked == 0) {
            document.getElementById('i-' + circleIds['classDays'].toString()).style.color = disabledColor;
        }
        else {
            document.getElementById('i-' + circleIds['classDays'].toString()).style.color = '';
        }
    })
     
};

distanceInput.addEventListener('change', function(){
    if (isFilled(distanceInput, "0")) {
        document.getElementById('i-' + circleIds['distance'].toString()).style.color = '';
    }
    else {
        document.getElementById('i-' + circleIds['distance'].toString()).style.color = disabledColor;
    }
});

probabilityInput.addEventListener('change', function(){
    if (isFilled(probabilityInput, "0.00")) {
        document.getElementById('i-' + circleIds['probability'].toString()).style.color = '';
    }
    else {
        document.getElementById('i-' + circleIds['probability'].toString()).style.color = disabledColor;
    }
});

probabilityInput.addEventListener('change', function(){
    if (isFilled(probabilityInput, "0", true)) {
        document.getElementById('i-' + circleIds['probability'].toString()).style.color = '';
    }
    else {
        document.getElementById('i-' + circleIds['probability'].toString()).style.color = disabledColor;
    }
});

probabilityRange.addEventListener('change', function(){
    if (isFilled(probabilityRange, "0", true)) {
        document.getElementById('i-' + circleIds['probability'].toString()).style.color = '';
    }
    else {
        document.getElementById('i-' + circleIds['probability'].toString()).style.color = disabledColor;
    }
});

function checkClassTime() {
    if (isFilled(earliestTimeInput) && isFilled(latestTimeInput)) {
        document.getElementById('i-' + circleIds['classTimes'].toString()).style.color = '';
    }
    else {
        document.getElementById('i-' + circleIds['classTimes'].toString()).style.color = disabledColor;
    }
}

earliestTimeInput.addEventListener('change', checkClassTime);

latestTimeInput.addEventListener('change', checkClassTime);

function checkBreakDuration() {
    if (isFilled(minBreakInput, "0") && isFilled(minBreakUnitInput) && isFilled(maxBreakInput, "0") && isFilled(maxBreakUnitInput)) {
        document.getElementById('i-' + circleIds['breakDuration'].toString()).style.color = '';
    }
    else {
        document.getElementById('i-' + circleIds['breakDuration'].toString()).style.color = disabledColor;
    }
}

minBreakInput.addEventListener("change", checkBreakDuration);
minBreakUnitInput.addEventListener("change", checkBreakDuration);
maxBreakInput.addEventListener("change", checkBreakDuration);
maxBreakUnitInput.addEventListener("change", checkBreakDuration);




