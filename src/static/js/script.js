let passwordInputOne = document.getElementById("id_password1")
passwordInputOne.addEventListener('input', updatePasswordStrength)
let passwordInputTwo = document.getElementById("id_password2")

function updatePasswordStrength() {
    let passwordLength = document.getElementById("passwordLength");
    let passwordNumeric = document.getElementById("passwordNumeric");
    let passwordCasing = document.getElementById("passwordCasing");
    let password = passwordInputOne.value;

    if (password.length > 8 && isAlphaNumeric(password)) {
        passwordLength.style.color = "blue";
    }
    else {
        passwordLength.style.color = "rgba(0,0,0,0.3)";
    }

    if (/\d/.test(password)) {
        passwordNumeric.style.color = "blue";
    }
    else {
        passwordNumeric.style.color = "rgba(0,0,0,0.3)";
    }

    if (hasUpperCase(password) && hasLowerCase(password)){
        passwordCasing.style.color = "blue";
    }
    else {
        passwordCasing.style.color = "rgba(0,0,0,0.3)";
    }
}

function isAlphaNumeric(str) {
    return /^[a-z0-9]+$/i.test(str);
}

function hasUpperCase(str) {
    return str !== str.toLowerCase();
}

function hasLowerCase(str) {
    return str !== str.toUpperCase();
}

let togglePasswordOne = document.getElementById("togglePasswordOne");
let togglePasswordTwo = document.getElementById("togglePasswordTwo");

togglePasswordOne.addEventListener("click", function(){togglePassword(1);});
togglePasswordTwo.addEventListener("click", function(){togglePassword(2);});

function togglePassword(n){
    if (n==1) {
        if (passwordInputOne.type == "password"){
            passwordInputOne.type = "text";
            togglePasswordOne.className = "bi-eye eye-icon";
        }
        else {
            passwordInputOne.type = "password";
            togglePasswordOne.className = "bi-eye-slash eye-icon";
        }
    }
    else {
        if (passwordInputTwo.type == "password"){
            passwordInputTwo.type = "text";
            togglePasswordTwo.className = "bi-eye eye-icon";
        }
        else {
            passwordInputTwo.type = "password";
            togglePasswordTwo.className = "bi-eye-slash eye-icon";
        }
    }
    
}