function copyJobTitle(){
    copyText('position-title-field', "job-title")
}


function copyCampaignDescription(){
    copyText('description', "campaign-description")
}


function long_form_disable(target) {

    var iframe_docs = getIframeDocs();

    //getIframeDocs
    iframe_docs[0].getElementById(target).disabled = true;
    iframe_docs[1].getElementById(target).disabled = true;
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

    var iframe_doc = getIframeDocs()[0];
    if (iframe_doc.getElementById(bullet_id)){
        // update
        copyText(bullet_id, bullet_id);
    }else{
        // create
        appendElement(vacancy_bullets, bullet_id);
        appendElement(company_bullets, bullet_id);
        copyText(bullet_id, bullet_id);
    }
}
