function ValidateForm(missing_name_alert, missing_email_alert, invalid_email_alert){
    var name = $('#name').val()
    var email = $('#email').val()

    if (name == "" || name  == null){
        alert(missing_name_alert);
        return false;
    }

    if (email == "" || email == null){
        alert(missing_email_alert);
        return false
    }

    if (!email.includes("@") || !email.includes(".")){
        alert(invalid_email_alert);
        return false
    }
}