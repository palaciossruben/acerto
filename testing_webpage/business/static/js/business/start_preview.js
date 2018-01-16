function get_iframes(){
    return document.getElementsByClassName('preview')
}

/*
Copies text from a Source element to a target element.
*/
function copy_text(source, target) {

    var my_iframes = get_iframes();
    var source_text = document.getElementById(source).value;

    my_iframes[0].contentWindow.document.getElementById(target).innerHTML = source_text;
    my_iframes[1].contentWindow.document.getElementById(target).innerHTML = source_text;
}

function copy_job_title(){
    copy_text('position-title-field', "job-title")
    copy_text('description_es', "campaign-description")
}

function long_form_disable(target) {

    var my_iframes = get_iframes();

    my_iframes[0].contentWindow.document.getElementById(target).disabled = true;
    my_iframes[1].contentWindow.document.getElementById(target).disabled = true;
}

function disables(){
    long_form_disable('name')
    long_form_disable('email')
    long_form_disable('phone')
    long_form_disable('country')
    long_form_disable('education')
    long_form_disable('profession')
    long_form_disable('file')
    long_form_disable('checkbox')
    long_form_disable('submit')
}

