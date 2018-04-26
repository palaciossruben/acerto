//global variable indicating the current question_number
var question_number = 1;

function addQuestionTypeSelector(container, question_types) {

    var question_type = document.createElement("select");
    question_type.name = question_number + "_new_question_type";
    question_type.required = true;
    container.appendChild(question_type);

    //Create and append the options
    var option = document.createElement("option");
    option.value = "";
    option.text = "Select an option";
    question_type.appendChild(option);

    for (var i = 0; i < question_types.length; i++) {
        var option = document.createElement("option");
        option.value = question_types[i].pk;
        option.text = question_types[i].fields.name;
        question_type.appendChild(option);
    }
}

function build_text_field(container, name, placeholder) {

    var text_input = document.createElement("input");
    text_input.type = "text";
    text_input.size = "100";
    text_input.name = name;
    text_input.placeholder = placeholder;
    container.appendChild(text_input);
}


function add_remove_button(container){

    var remove_button = document.createElement("input");
    remove_button.type = "button";
    remove_button.class = "btn btn-danger";
    remove_button.value = "Delete!";
    remove_button.onclick = "deleteQuestion(" + question_number + ")";
    container.appendChild(remove_button);
}


function build_question_ui(container, question_types) {

    container.appendChild(document.createElement("br"));
    container.appendChild(document.createTextNode("Question " + question_number));

    container.appendChild(document.createElement("br"));

    build_text_field(container, question_number + "_new_question_name", "add text in english");

    container.appendChild(document.createElement("br"));

    build_text_field(container, question_number + "_new_question_name_es", "add text in spanish");

    container.appendChild(document.createElement("br"));

    addQuestionTypeSelector(container, question_types);

    add_remove_button(container);

    container.appendChild(document.createElement("br"));
    container.appendChild(document.createElement("br"));
}


function addQuestion(question_types){
    /*
    Adds a question to the interface and numbers it.
    */
    question_types = JSON.parse(question_types)

    var container = document.getElementById("question_container");

    build_question_ui(container, question_types);

    //adds 1 for next question.
    question_number = question_number + 1
}
