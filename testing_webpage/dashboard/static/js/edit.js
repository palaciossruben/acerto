function send_candidate_id_in_params(candidate_id)   {

    form = document.getElementById('main_form_id');

    myvar = document.createElement('input');
    myvar.setAttribute('name', 'candidate_id_changed');
    myvar.setAttribute('type', 'hidden');
    myvar.setAttribute('value', candidate_id);
    form.appendChild(myvar);
    document.body.appendChild(form);
    form.submit();
}
