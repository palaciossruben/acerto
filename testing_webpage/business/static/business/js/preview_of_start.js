function get_iframes(){
    return document.getElementsByClassName('preview')
}

function copyJobTitle(){
    copyText('position-title-field', "job-title")
}


function copyCampaignDescription(){
    copyText('description', "campaign-description")
}


function long_form_disable(target) {

    var my_iframes = get_iframes();

    my_iframes[0].contentWindow.document.getElementById(target).disabled = true;
    my_iframes[1].contentWindow.document.getElementById(target).disabled = true;
}

function disables(){
    long_form_disable('name')
    long_form_disable('email')
    long_form_disable('phone')
    long_form_disable('country')
    long_form_disable('education')
    long_form_disable('profession')
    long_form_disable('file')
    long_form_disable('checkbox')
    long_form_disable('submit')
}


// -------------------------------------------------- Bullet Display ------------------------------------------------ //


function getListItems(list_id, type, iframe_id) {

    var list_id = type + '-bullets-list';

    var list = document.getElementById(iframe_id).contentWindow.document.getElementById(list_id);

    if (!list){
        throw 'Unimplemented bullet type for preview display.';
    }

    return list;
}




function getBulletNumber(bullet_id){

    // Starting with integer regex.
    var r = /^\d+/;

    var my_match = bullet_id.match(r);

    if (my_match){
        // Convert to int
        return parseInt(my_match[0]);
    }else{
        // No match found
        return 0;
    }
}


function appendElement(bullets, bullet_id) {

    var bullet = document.getElementById(bullet_id);

    var element = document.createElement("li");
    element.name = bullet.value;
    element.value = bullet.value;
    element.id = bullet.id;
    bullets.appendChild(element);
}


function getBulletType(bullet_id){
    return bullet_id.split('_').pop();
}


/*
Counts items in a ul list. Uses JQuery.
*/
function countItems(list_id){
    return $("#vacancy_iframe").contents().find("#" + list_id + " li").length
}


function getListId(type){
    return type + '-bullets-list';
}

function editPreviewBullets(bullet_id) {

    var bullet_num = getBulletNumber(bullet_id);
    var type = getBulletType(bullet_id);
    var list_id = getListId(type);
    var vacancy_bullets = getListItems(list_id, type, 'vacancy_iframe');
    var company_bullets = getListItems(list_id, type, 'company_iframe');

    if (countItems(list_id) >= bullet_num) {
        // update
        copyText(bullet_id, bullet_id);
    }else{
        // create
        appendElement(vacancy_bullets, bullet_id);
        appendElement(company_bullets, bullet_id);
    }

    var int_to_string = bullet_num + 1;
    var str1 =  '' + int_to_string;
    var str2 = "_requirement";
    var concat_id = str1.concat(str2);

    document.getElementById(concat_id).disabled = false;
}
