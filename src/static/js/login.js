/* Login Components */

let passwordLogin = document.getElementById("id_password");
let toggleLoginPassword = document.getElementById("toggleLoginPassword");

/* Checks if user chose to reveal/hide their password */
function togglePassword(passwordField, toggleIcon){
    if (passwordField.type == "password") {
        passwordField.type = "text";
        toggleIcon.className = "bi-eye eye-icon";
    }
    else {
        passwordField.type = "password";
        toggleIcon.className = "bi-eye-slash eye-icon";
    }
}

toggleLoginPassword.addEventListener("click", function(){togglePassword(passwordLogin, toggleLoginPassword);});

function renderLoading() {
    var loading = document.getElementById("loader");
    loading.style.display = "block";
}