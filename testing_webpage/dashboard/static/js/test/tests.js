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
    option.text = "Seleccione una opción";
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
    remove_button.name = "remove_btn" + question_number
    remove_button.type = "button";
    remove_button.class = "btn btn-danger";
    remove_button.value = "Borrar";
    remove_button.onclick = "deleteQuestion(" + question_number + ")";
    container.appendChild(remove_button);
}


function build_question_ui(container, question_types) {

    container.appendChild(document.createElement("br"));
    container.appendChild(document.createTextNode("Pregunta " + question_number));

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

function addQuestion(){
    /*
    Adds a question to the interface and numbers it.
    */

    // Number of inputs to create
    var container = document.getElementById("question_container");

    // Append a node with a random text
    //container.appendChild(document.createElement("br"));
    //container.appendChild(document.createTextNode("Pregunta " + question_number + " "));

    var text_input = document.createElement("input");

    text_input.type = "text";
    text_input.style.width = "500px"
    text_input.name = "question_name" + question_number;
    var questionName = "question_name" + question_number;
    container.appendChild(text_input);
    var remove_button = document.createElement("input");

    remove_button.type = "button";
    remove_button.class = "btn btn-danger"
    remove_button.value = "Borrar"
    remove_button.name = "question_del" + question_number;
    var questiondelName = "question_del" + question_number;
    container.appendChild(remove_button);
    container.appendChild(document.createElement("br"));
    remove_button.onclick = deleteQuestion(questionName, questiondelName);
    
    // Append a line break
    container.appendChild(document.createElement("br"));

    question_number = question_number + 1
}

function deleteQuestion(questionName, questionDel){
    var container = document.getElementById("question_container");    
    container.removeChild(document.getElementsByName("'" + questionDel + "'"););
    container.removeChild(document.getElementsByName("'" + questionName + "'");)
    question_number = question_number - 1
}