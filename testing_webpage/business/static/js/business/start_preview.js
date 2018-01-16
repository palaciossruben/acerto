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

function long_form_disable(iframe_index) {

    var my_iframes = document.getElementsByClassName('preview')
    my_iframes[iframe_index].contentWindow.document.getElementById("name").disabled = true;
}

