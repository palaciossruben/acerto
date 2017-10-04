var question_number = 1;

function addQuestion(){
    /*
    Adds a question to the interface and numbers it.
    */

    // Number of inputs to create
    //var number = document.getElementById("member").value;
    // Container <div> where dynamic content will be placed
    var container = document.getElementById("question_container");

    // Append a node with a random text
    container.appendChild(document.createElement("br"));
    container.appendChild(document.createTextNode("Question " + question_number + " "));

    var text_input = document.createElement("input");
    text_input.type = "text";
    text_input.style.width = "500px"
    text_input.name = "question_name" + question_number;
    container.appendChild(text_input);

    var remove_button = document.createElement("input");
    remove_button.type = "button";
    remove_button.class = "btn btn-danger"
    remove_button.value = "Delete!"
    container.appendChild(remove_button);

    //<input type="button" name="remove_from_campaign"
    //onclick="send_additional_params_in_form({{ candidate.id }}, 'remove')">


    container.appendChild(remove_button);
    // Append a line break
    container.appendChild(document.createElement("br"));

    question_number = question_number + 1
}
