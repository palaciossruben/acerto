var question_number = 1;
var mapQuestion = {};

function addQuestion(question_types_json){

    var container = document.getElementById("question_container");
    var jsonList = "{{qtypes_json}}";

    var division = document.createElement("div");
    division.id = 'block' + question_number;
    division.className = 'block';

    var dropQuestion = document.createElement("select")


    for (var v in question_types_json){
        var opt = v;
        var el = documnent.createElement("option");
        el.textContent = opt;
        el.value = opt;
        select-appendChild(el);
    }

    division.appendChild(dropQuestion);
    
    var text_input = document.createElement("input");
    text_input.type = "text";
    text_input.style.width = "500px"
    text_input.id = "question_name" + question_number;    
    division.appendChild(text_input);

    var remove_button = document.createElement("input");
    remove_button.type = "button";
    remove_button.class = "btn btn-danger"
    remove_button.value = "Borrar"
    remove_button.id = "question_del" + question_number;
    var questiondelName = "question_del" + question_number;    
    division.appendChild(remove_button);
    var separator = document.createElement("br");
    container.appendChild(separator);
    remove_button.onclick = function(){deleteQuestion(this);};    
    
    // Append a line break
    division.appendChild(document.createElement("br"));
    container.appendChild(division);
    mapQuestion['block' + question_number] = division;
    question_number = question_number + 1;
}

function deleteQuestion(obj){

    var caller = obj;
    var btnContainer = caller.parentNode;        
    var container = document.getElementById("question_container");    
    var divPosition = btnContainer.id + "";
    var blockQuestion = document.getElementById(divPosition);
    question = mapQuestion[divPosition];
    //var element = container.childNodes.item(blockQuestion.id);    
    blockQuestion.parentNode.removeChild(blockQuestion);
    //mapQuestion.remove(divPosition);
    question_number = question_number - 1
}

function submitForm(){
    
}
