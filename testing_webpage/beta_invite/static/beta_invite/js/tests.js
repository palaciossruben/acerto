function activate(test_number, question_number){
    $('#container-'+test_number+'-'+question_number).css({'display': 'block'});
}

function deactivate(test_number, question_number){
    $('#container-'+test_number+'-'+question_number).css({'display': 'none'});
}

function back(test_number, question_number, last_test_number_of_questions){
    if (question_number == 1) {
        activate(test_number -1, last_test_number_of_questions);
    }else{
        activate(test_number, question_number - 1);
    }
    deactivate(test_number, question_number);
}

function next(test_number, question_number, number_of_questions, number_of_tests){

    if (question_number == number_of_questions) {
        activate(test_number +1, 1);
    }else{
        activate(test_number, question_number + 1);
    }

    if (test_number == number_of_tests && question_number == number_of_questions - 1){
        $('#submit-button').css({'display': 'block'});
    }
    deactivate(test_number, question_number);
}

function timer(){
    var minutesLabel = document.getElementById("minutes");
    var secondsLabel = document.getElementById("seconds");
    var totalSeconds = 0;
    setInterval(setTime, 1000);

    function setTime() {
        ++totalSeconds;
        secondsLabel.innerHTML = pad(totalSeconds % 60);
        minutesLabel.innerHTML = pad(parseInt(totalSeconds / 60));
    }

    function pad(val) {
        var valString = val + "";
        if (valString.length < 2) {
            return "0" + valString;
        } else {
            return valString;
        }
    }
}