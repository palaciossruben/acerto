var QUESTION_NUMBER = 1;

// Dictionary of the form {question_number: answer_number}
var ANSWER_NUMBERS = {};

function get_selected_type(question_types){
    /*
     "open field"
     "single answer"
     "degree of belief"
     "Numeric Integer"
     "multiple answer"
    */

    var selected_type_id = parseInt(document.getElementById("question_type").value);
    var selected_type = _.filter(question_types, {"pk": selected_type_id})[0];

    return selected_type;
}


function addQuestionTextArea(container, question_name, placeholder){
    var my_text_area = document.createElement("textarea");
    my_text_area.cols = "120";
    my_text_area.rows = "5";
    my_text_area.name = question_name;
    my_text_area.placeholder = placeholder
    container.appendChild(my_text_area);
}


function addFileInput(container, question_number){

    var image_input = document.createElement("input");
    image_input.id = "file";
    image_input.type = "file";
    image_input.value = "";
    image_input.className = "form-inputfile";
    image_input.onchange = "pressed()";
    image_input.name = get_question_name(question_number, "image_path");
    container.appendChild(image_input);

    var file_label = document.createElement("label");
    file_label.for = "file";
    file_label.id = "fileLabel";
    file_label.value = "Upload image (optional)"
    container.appendChild(file_label);
}


function addBr(container){container.appendChild(document.createElement("br"));}
function addHr(container){container.appendChild(document.createElement("hr"));}


function addQuestionRemoveButton(container, question_number){
    var remove_button = document.createElement("input");
    remove_button.type = "button";
    remove_button.className = "btn btn-danger";
    remove_button.value = "Delete Question!";
    remove_button.onclick = function() { eraseQuestion(question_number); };
    container.appendChild(remove_button);
}


function addAnswerRemoveButton(container, question_number, answer_number){
    var remove_button = document.createElement("input");
    remove_button.type = "button";
    remove_button.className = "btn btn-danger";
    remove_button.value = "Delete Answer!";
    remove_button.onclick = function() { eraseAnswer(question_number, answer_number); };
    container.appendChild(remove_button);
}


function buildTextField(container, name, placeholder) {

    var text_input = document.createElement("input");
    text_input.type = "text";
    text_input.size = "80";
    text_input.name = name;
    text_input.placeholder = placeholder;
    container.appendChild(text_input);
}


function buildCheckbox(container, name){

    var checkbox_input = document.createElement("input");
    checkbox_input.name = name;
    checkbox_input.type = "checkbox";
    checkbox_input.value = "off";
    checkbox_input.onclick = function() { toggle_checkbox_value(this); };
    container.appendChild(checkbox_input);
}


function get_answer_name(question_number, answer_number_json, suffix){
    /*
    Follows the <object_id>_<class_name>_<attribute_name> recursive format processed on backend
    */

    if (suffix == '') {
        var answer_word = "_answer"
    }else{
        var answer_word = "_answer_"
    }
    return get_question_name(question_number, answer_number_json[question_number] + answer_word + suffix);
}


function get_question_name(question_number, suffix){
    /*
    Follows the <object_id>_<class_name>_<attribute_name> recursive format processed on backend
    */
    if (suffix == '') {
        var question_word = "_question"
    }else{
        var question_word = "_question_"
    }
    return question_number + question_word + suffix;
}


function buildAnswerUi(answer_container, question_number) {

    addBr(answer_container);
    answer_container.appendChild(document.createTextNode("Answer " + ANSWER_NUMBERS[question_number]));

    addBr(answer_container);
    buildCheckbox(answer_container, get_answer_name(question_number, ANSWER_NUMBERS, "is_correct"));

    addBr(answer_container);
    buildTextField(answer_container, get_answer_name(question_number, ANSWER_NUMBERS, "name"), "add text in English");

    addBr(answer_container);
    buildTextField(answer_container, get_answer_name(question_number, ANSWER_NUMBERS, "name_es"), "add text in Spanish");

    addBr(answer_container);
    addAnswerRemoveButton(answer_container, question_number, ANSWER_NUMBERS[question_number]);

    addBr(answer_container);addBr(answer_container);
}


function update_answer_numbers(question_number){
    //adds 1 for next answer, given a question_number.
    if (ANSWER_NUMBERS[question_number]){
        ANSWER_NUMBERS[question_number] = ANSWER_NUMBERS[question_number] + 1;
    }else{
        var container_name = get_question_name(question_number, "answer_container");
        var question_answer_container = document.getElementById(container_name);

        if (question_answer_container){
            ANSWER_NUMBERS[question_number] = question_answer_container.childElementCount + 1;
        } else {
            ANSWER_NUMBERS[question_number] = 1;
        }
    }
}


function addAnswer(question_number){
    /*
    Adds a answer interface and numbers it.
    */

    //Given question_number, will attach to a answer_container
    var container_name = get_question_name(question_number, "answer_container");
    var question_answer_container = document.getElementById(container_name);

    update_answer_numbers(question_number)

    var answer_container = document.createElement("div");
    answer_container.id = get_answer_name(question_number, ANSWER_NUMBERS, '');
    question_answer_container.appendChild(answer_container)

    buildAnswerUi(answer_container, question_number);
}


function addSingleAnswerCustomization(container, question_number){

    container.appendChild(document.createComment("This empty container is filled dynamically with JS"));
    var answer_container = document.createElement("div");
    answer_container.id = get_question_name(question_number, "answer_container");
    container.appendChild(answer_container)

    var button = document.createElement("input");
    button.type = "button";
    button.size = "80";
    button.name = "add_answer";
    button.className = "btn btn-success";
    button.value = "Add answer";
    button.onclick = function() { addAnswer(question_number); };
    container.appendChild(button);

    addBr(container);addBr(container);

}


function addQuestionType(question_number, container, selected_type) {
    var hidden_input = document.createElement("input");
    hidden_input.name = get_question_name(question_number, "type_id");
    hidden_input.value = selected_type.pk;
    hidden_input.hidden = true;
    container.appendChild(hidden_input);
}


function get_number_of_questions(all_questions_container){
    return all_questions_container.children.length;
}


function get_question_number(all_questions_container){
    /*
        Gets the question_number to be assigned on the new question. It should always be the highest_id + 1
    */

    // the current biggest div question id found.
    biggest_id = 0;
    var children = all_questions_container.children;
    for (var i = 0; i < children.length; i++) {
        var question = children[i];
        var question_id = parseInt(question.getAttribute("id").split("_")[0]);
        biggest_id = Math.max(question_id, biggest_id);
    }
    return biggest_id + 1
}


function addsIntegerInput(container, input_name, title){

    var my_div = document.createElement('div');
    addBr(my_div); addBr(my_div);
    my_div.appendChild(document.createTextNode(title));
    addBr(my_div);
    var number_input = document.createElement('input');

    number_input.type = 'number';
    number_input.value = 0; // default value
    number_input.min = -99999999;
    number_input.max = 99999999;
    number_input.name = input_name;

    my_div.appendChild(number_input);
    container.appendChild(my_div);
}


function addIntegerQuestion(question_container, question_number){

    var integer_div = document.createElement('div')

    //Adds min value selector.
    addsIntegerInput(integer_div, get_question_name(question_number, 'min'), 'Add smallest value that the user can choose from');

    //Adds max value selector.
    addsIntegerInput(integer_div, get_question_name(question_number, 'max'), 'Add biggest value that the user can choose from');

    //Adds min_correct value selector.
    addsIntegerInput(integer_div, get_question_name(question_number, 'min_correct'), 'Add minimum correct value');

    //Adds max_correct value selector.
    addsIntegerInput(integer_div, get_question_name(question_number, 'max_correct'), 'Add maximum correct value');

    //Adds max value selector.
    addsIntegerInput(integer_div, get_question_name(question_number, 'default'), 'Add the default value of the selector');

    question_container.appendChild(integer_div);
}


function addQuestion(question_types){
    /*
    Adds a question to the interface and numbers it.
    param question_types: json with the possible types, defined in django fixture.
    param number_of_questions: The number of previous questions, its 0 for new tests.
    */

    var question_types = JSON.parse(question_types);
    var all_questions_container = document.getElementById("question_container");

    QUESTION_NUMBER = get_question_number(all_questions_container);

    var question_container = document.createElement("div");
    question_container.id = QUESTION_NUMBER + "_question"
    all_questions_container.appendChild(question_container)

    selected_type = get_selected_type(question_types);

    if (selected_type) {

        addBr(question_container);
        question_container.appendChild(document.createTextNode("Question " + QUESTION_NUMBER + " "));

        addBr(question_container);

        question_container.appendChild(document.createTextNode("Excluding?"));
        buildCheckbox(question_container, get_question_name(QUESTION_NUMBER, "excluding"));

        addBr(question_container);addBr(question_container);

        var text_name = get_question_name(QUESTION_NUMBER, "text")
        addQuestionTextArea(question_container, text_name, "Question in English")

        addBr(question_container);addBr(question_container);

        var text_name_es = get_question_name(QUESTION_NUMBER, "text_es")
        addQuestionTextArea(question_container, text_name_es, "Question in Spanish")

        addBr(question_container);addBr(question_container);

        addFileInput(question_container, QUESTION_NUMBER);

        addBr(question_container);

        if (selected_type.fields.name == "single answer"){
            addSingleAnswerCustomization(question_container, QUESTION_NUMBER)
        }else if (selected_type.fields.name == "numeric integer"){
            addIntegerQuestion(question_container, QUESTION_NUMBER)
        }

        addBr(question_container);addBr(question_container);

        addQuestionRemoveButton(question_container, QUESTION_NUMBER);

        addBr(question_container); addBr(question_container);
        addHr(question_container);

        addQuestionType(QUESTION_NUMBER, question_container, selected_type);

        QUESTION_NUMBER = QUESTION_NUMBER + 1;

    } else {
        alert("Specify a question type before adding a new Question")
    }
}


function toggle_checkbox_value(checkbox){
    if (checkbox.value == "on"){
        checkbox.value = "off"
        checkbox.checked = false;
    }else {
        checkbox.value = "on"
        checkbox.checked = true;
    }
}


function deleteQuestion(question_id, question_number){
    /*
        Sends info to backend delete question from test with ajax. This is only when question has already been saved on
        DB
    */
    param_dict = {'question_id': question_id}
    general_dict = {csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()}

    $.ajax({
        type:'POST',
        url:'delete_question',
        data: Object.assign({}, general_dict, param_dict),
        cache: false,
        success: function(){
            eraseQuestion(question_number)
        } });
}


function eraseQuestion(question_number){
    /*
    Erase the question in JS
    */
    $("#" + question_number + "_question").remove();
}


function deleteAnswer(answer_id, question_number, answer_number){
    /*
        Sends info to backend delete question from test with ajax. This is only when question has already been saved on
        DB
    */
    param_dict = {'answer_id': answer_id}
    general_dict = {csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()}

    $.ajax({
        type:'POST',
        url:'delete_answer',
        data: Object.assign({}, general_dict, param_dict),
        cache: false,
        success: function(){
            eraseAnswer(question_number, answer_number)
        } });
}


function eraseAnswer(question_number, answer_number){
    /*
    Erase the answer in JS
    */
    $("#" + question_number + "_question_" + answer_number + "_answer").remove();
}
