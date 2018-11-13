function set_circle_color(score, id_string){

    var color;

    if (score < 50){
        color = 'rgba(221, 81, 51,';
    }else if (score < 59){
        color = 'rgba(232, 144, 61,';
    }else if (score < 69){
        color = 'rgba(238, 165, 64,';
    }else if (score < 74){
        color = 'rgba(247, 212, 71,';
    }else if (score < 79){
        color = 'rgba(251, 212, 71,';
    }else if (score < 84){
        color = 'rgba(255, 230, 73,';
    }else if (score < 89){
        color = 'rgba(224, 225, 89,';
    }else if (score < 94){
        color = 'rgba(172, 203, 84,';
    }else if (score < 99){
        color = 'rgba(72, 171, 88,';
    }else{
        color = 'rgba(74, 180, 166,';
    }

    if (score === null){
    }else{
        var me = document.getElementById(id_string);
        if(me == null){
        }else{
            me.style["border-color"] = color + '1)';
            me.style["background"] = 'linear-gradient(to top,' + color + '0.7)' + score + '%, transparent ' + score + '% )';
        }
    }
}

function set_background(image_name, id_string){

    image_name = image_name.replace("&#39;","");
    if (image_name == 'default' || image_name == ''){
        image_name = "Start_BG-07.jpg)"
    }

    var me = document.getElementById(id_string);
    if(me == null){
    }else{
        if ($(window).width() < 768) {
        image_name = 'cel-' + image_name;
        var url = 'url(../../../../../static/business/img/' + image_name;
        me.style["background-image"] = url;
    }else{
        var url = 'url(../../../../../static/business/img/min-' + image_name;
        me.style["background-image"] = url;
    }}
}

function not_blocked(business_state, free_trial, campaign_state){

    var limit = 0;

    if (free_trial == 'False'){
        limit = 0;
    }
    else if(free_trial == 'True' && campaign_state != "Inactive" ){
        if (business_state == 'aplicantes'){
            limit = 10;
        }else{
            limit = 1;
        }
    }else{
        limit = 0;
    }

    var candidate_divs= $('.candidate-div a');
    for (var i = 0; i < limit; i++) {
        $(candidate_divs[i]).attr('href', $(candidate_divs[i]).attr('href').replace('/remove',''));
        $(candidate_divs[i]).attr('onclick', "");

    }
    var candidate_divs= $('.candidate-div span');
    for (var i = 0; i < limit; i++) {
        $(candidate_divs[i]).hide();
    }
}