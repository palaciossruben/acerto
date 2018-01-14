function preview() {
    var position_title = document.getElementById('position-title-field').value;
    var my_iframes = document.getElementsByClassName('preview')

    my_iframes[0].contentWindow.document.getElementById("job-title").innerHTML = position_title;
    //my_iframes[1].contentWindow.document.getElementById("preview_test").innerHTML = position_title;
}

function long_form_disable() {

    var my_iframes = document.getElementsByClassName('preview')
    my_iframes[0].contentWindow.document.getElementById("name").disabled = true;
    //my_iframes[1].contentWindow.document.getElementById("name").disable = true;
}



