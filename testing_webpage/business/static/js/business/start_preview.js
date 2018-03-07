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

function preview_disable(target) {

    var my_iframes = get_iframes();

    my_iframes[0].contentWindow.document.getElementById(target).disabled = true;
    my_iframes[1].contentWindow.document.getElementById(target).disabled = true;
}

function disables(){
    preview_disable('name')
    preview_disable('email')
    preview_disable('phone')
    preview_disable('country')
    preview_disable('education')
    preview_disable('profession')
    preview_disable('file')
    preview_disable('checkbox')
    preview_disable('submit')
}

