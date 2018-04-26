var question_number = 1;


function get_selected_type(question_types){
    /*
     "single answer"
     "open field"
     "degree of belief"
     "Numeric Integer"
     "multiple answer"
    */

    var selected_type_id = parseInt(document.getElementById("question_type").value);
    var selected_type = _.filter(question_types, {"pk": selected_type_id})[0];

    console.log(selected_type);

    return selected_type;
}


function addQuestionTextArea(container, question_name, placeholder){
    var my_text_area = document.createElement("textarea");
    my_text_area.cols = "120";
    my_text_area.rows = "5";
    my_text_area.name = question_name;
    my_text_area.placeholder = placeholder
    container.appendChild(my_text_area);

    return container
}

function addQuestion(question_types, number_of_questions){
    /*
    Adds a question to the interface and numbers it.
    param question_types: json with the possible types, defined in django fixture.
    param number_of_questions: The number of previous questions, its 0 for new tests.
    */
    question_number = Math.max(question_number, number_of_questions + 1)

    var question_types = JSON.parse(question_types);
    var container = document.getElementById("question_container");

    selected_type = get_selected_type(question_types);

    if (selected_type) {

        //Append br and question number
        container.appendChild(document.createElement("br"));
        container.appendChild(document.createTextNode("Question " + question_number + " "));

        container = addQuestionTextArea(container, question_number + "_question_text", "Question in English")

        container.appendChild(document.createElement("br"));
        container.appendChild(document.createElement("br"));

        container = addQuestionTextArea(container, question_number + "_question_text_es", "Question in Spanish")

        container.appendChild(document.createElement("br"));
        container.appendChild(document.createElement("br"));

        var image_input = document.createElement("input");
        image_input.id = "file";
        image_input.type = "file";
        image_input.value = "";
        image_input.className = "form-inputfile";
        image_input.onchange = "pressed()";
        image_input.name = question_number + "_question_image";
        container.appendChild(image_input);

        var file_label = document.createElement("label");
        file_label.for = "file";
        file_label.id = "fileLabel";
        file_label.value = "Upload image (optional)"
        container.appendChild(file_label);

        container.appendChild(document.createElement("br"));

        var remove_button = document.createElement("input");
        remove_button.type = "button";
        remove_button.className = "btn btn-danger";
        remove_button.value = "Delete!";
        container.appendChild(remove_button);

        var question_type_input = document.createElement("input");
        question_type_input.type = "hidden";
        question_type_input.value = selected_type.pk;
        question_type.name = question_number + "question_type";
        container.appendChild(question_type_input);

        container.appendChild(document.createElement("br"));

        question_number = question_number + 1;

    } else {
        alert("Specify a question type before adding a new Question")
    }
}
