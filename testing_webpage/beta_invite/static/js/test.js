function add_checked_values(questions_dict){

    form = document.getElementById('test_form_id');

    for (var test_id in questions_dict) {
        if (questions_dict.hasOwnProperty(test_id) {

            test_questions_ids = questions_dict[test_id];

            radio_name = "test_" + test_id + "_question_" + question_id

            var answers = document.getElementsByName(radio_name);
            var selected_answer;
            for(var i = 0; i < answers.length; i++){
                if(answers[i].checked){
                    selected_answer = answers[i].value;
                }
            }

            radio_input = document.createElement('input');
            radio_input.setAttribute('name', radio_name);
            radio_input.setAttribute('type', 'hidden');
            radio_input.setAttribute('value', selected_answer);
            form.appendChild(radio_input);
        }
    }
}