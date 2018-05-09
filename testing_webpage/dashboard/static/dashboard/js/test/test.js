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


function addRemoveButton(container){
    var remove_button = document.createElement("input");
    remove_button.type = "button";
    remove_button.className = "btn btn-danger";
    remove_button.value = "Delete Question!";
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
    checkbox_input.value="incorrect";
    checkbox_input.onclick=function() { toggle_checkbox_value(this); };
    container.appendChild(checkbox_input);
}


function get_answer_name(question_number, answer_number_json, suffix){
    /*
    Follows the <object_id>_<class_name>_<attribute_name> recursive format processed on backend
    */
    return get_question_name(question_number, answer_number_json[question_number] + "_answer_" + suffix);
}


function get_question_name(question_number, suffix){
    /*
    Follows the <object_id>_<class_name>_<attribute_name> recursive format processed on backend
    */
    return question_number + '_question_' + suffix;
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

    //TODO: add remove button
    /*
    <input class="btn btn-danger" type="button" name="remove_answer" value="Add answer"
               onclick="removeAnswer('requirement');">
    */
    //add_remove_button(container);

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


function addAnswer(question_number){//, answer_container){
    /*
    Adds a answer interface and numbers it.
    */

    //Given question_number, will attach to a answer_container
    var container_name = get_question_name(question_number, "answer_container");
    var question_answer_container = document.getElementById(container_name);

    update_answer_numbers(question_number)

    var answer_container = document.createElement("div");
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
    container.appendChild(hidden_input);
}

function addQuestion(question_types, number_of_questions){
    /*
    Adds a question to the interface and numbers it.
    param question_types: json with the possible types, defined in django fixture.
    param number_of_questions: The number of previous questions, its 0 for new tests.
    */
    QUESTION_NUMBER = Math.max(QUESTION_NUMBER, number_of_questions + 1)

    var question_types = JSON.parse(question_types);
    var container = document.getElementById("question_container");

    selected_type = get_selected_type(question_types);

    if (selected_type) {

        addBr(container);
        container.appendChild(document.createTextNode("Question " + QUESTION_NUMBER + " "));

        addBr(container);addBr(container);

        var text_name = get_question_name(QUESTION_NUMBER, "text")
        addQuestionTextArea(container, text_name, "Question in English")

        addBr(container);addBr(container);

        var text_name_es = get_question_name(QUESTION_NUMBER, "text_es")
        addQuestionTextArea(container, text_name_es, "Question in Spanish")

        addBr(container);addBr(container);

        addFileInput(container, QUESTION_NUMBER);

        addBr(container);

        if (selected_type.fields.name == "single answer"){

            addSingleAnswerCustomization(container, QUESTION_NUMBER)
        }else if (selected_type.name == "numeric integer"){
            // TODO: implement
        }

        addBr(container);addBr(container);

        addRemoveButton(container);

        addBr(container);

        addQuestionType(QUESTION_NUMBER, container, selected_type);

        QUESTION_NUMBER = QUESTION_NUMBER + 1;

    } else {
        alert("Specify a question type before adding a new Question")
    }
}


function toggle_checkbox_value(checkbox){
    if (checkbox.value == "correct"){
        checkbox.value = "incorrect"
    }else {
        checkbox.value = "correct"
    }
}


function deleteQuestion(question_id, test_id){
    /*
        Sends info to backend delete question from test with ajax. This is only when question has already been saved on
        DB
    */
    param_dict = {'question_id': question_id,
                  'test_id': test_id}
    general_dict = {csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()}

    $.ajax({
        type:'POST',
        url:'delete_question',
        data: Object.assign({}, general_dict, param_dict),
        cache: false,
        success: function(){
            window.location.href = window.location.href;  // Reloads the UI
        } });
}
