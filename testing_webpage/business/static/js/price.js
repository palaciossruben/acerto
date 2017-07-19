function HoverOnStandard(){
    $('#standard_header').css("background", "green");
    $('#agile_header').css("background", "black");
    $('#custom_header').css("background", "black");
}

function HoverOnAgile(){
    $('#standard_header').css("background", "black");
    $('#agile_header').css("background", "green");
    $('#custom_header').css("background", "black");
}

function HoverOnCustom(){
    $('#standard_header').css("background", "black");
    $('#agile_header').css("background", "black");
    $('#custom_header').css("background", "green");
}

// great answer in: https://stackoverflow.com/questions/133925/javascript-post-request-like-a-form-submit
function Post(path, params, method) {
    method = method || "post"; // Set method to post by default if not specified.

    // The rest of this code assumes you are not using a library.
    // It can be made less wordy if you use one.
    var form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", path);

    for(var key in params) {
        if(params.hasOwnProperty(key)) {
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);

            form.appendChild(hiddenField);
         }
    }

    document.body.appendChild(form);
    form.submit();
}
