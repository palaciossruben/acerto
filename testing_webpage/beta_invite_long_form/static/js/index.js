function ValidateForm(missing_name_alert, missing_email_alert, invalid_email_alert, missing_curriculum){
    var name = $('#name').val()
    var email = $('#email').val()
    var curriculum = $('#curriculum').get(0).files

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

    if (curriculum.length === 0) {
        alert(missing_curriculum);
        return false;
    }
}