

/* Checks if user chose to reveal/hide their password */
// function togglePassword(passwordField, toggleIcon){
//     if (passwordField.type == "password") {
//         passwordField.type = "text";
//         toggleIcon.className = "bi-eye eye-icon";
//     }
//     else {
//         passwordField.type = "password";
//         toggleIcon.className = "bi-eye-slash eye-icon";
//     }
// }


/* console.log(toggleLoginPassword.className); */

// for overlays
function overlayOff() {
    document.getElementById("overlay").style.display = "none";
}

document.getElementById("submitClear").addEventListener("click", function() {
    // event.preventDefault()
    document.getElementById("clearOverlay").style.display = "block";
});

document.getElementById("clearYes").addEventListener("click", function() {
    document.getElementById('clearDCP').submit();
});

document.getElementById("clearNo").addEventListener("click", function() {
    document.getElementById("clearOverlay").style.display = "none";
});