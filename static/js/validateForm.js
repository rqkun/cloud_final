function validate() {
    var pass = document.getElementById("password").value;
    var cpass = document.getElementById("cpassword").value;
    var errormessage= document.getElementById("error-message");
    if (pass == cpass){
        
        if (/[A-Z]/.test(pass) == false){
            errormessage.removeAttribute("hidden");
            return false;
        }
        if (/[a-z]/.test(pass) == false){
            errormessage.removeAttribute("hidden");
            return false;
        }
        if (/[0-9]/.test(pass) == false){
            errormessage.removeAttribute("hidden");
            return false;
        }
        if (pass.length < 8){
            errormessage.removeAttribute("hidden");
            return false;
        }
        return true;
    } else {
        alert("Passwords do not match");
        return false;
    }
    
}


