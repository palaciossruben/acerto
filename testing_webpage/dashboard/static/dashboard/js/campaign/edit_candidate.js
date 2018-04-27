function send_additional_params_in_form(candidate_id, action)   {

    form = document.getElementById('main_form_id');

    myvar = document.createElement('input');
    myvar.setAttribute('name', 'candidate_id');
    myvar.setAttribute('type', 'hidden');
    myvar.setAttribute('value', candidate_id);
    form.appendChild(myvar);

    myvar = document.createElement('input');
    myvar.setAttribute('name', 'action');
    myvar.setAttribute('type', 'hidden');
    myvar.setAttribute('value', action);
    form.appendChild(myvar);

    document.body.appendChild(form);
    form.submit();
}


function selectAll(master_checkbox, column_candidates){
    /*
    Works as a master checkbox for an entire column
    */

    for (key in column_candidates){
        candidate = column_candidates[key]
        $('#' + candidate.pk + '_checkbox').prop('checked', master_checkbox.checked);
    }
}
