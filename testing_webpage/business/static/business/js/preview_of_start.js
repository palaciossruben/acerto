function copyJobTitle(){
    copyText('position-title-field', "job-title")
}


function copyCampaignDescription(){
    copyText("description", "campaign-description")
}


function preview_disable(target) {

    var iframe_docs = getIframeDocs();

    //getIframeDocs
    iframe_docs[0].getElementById(target).disabled = true;
    iframe_docs[1].getElementById(target).disabled = true;
}

function disables(){
    preview_disable('name')
    preview_disable('email')
    preview_disable('phone')
    preview_disable('country')
    preview_disable('education')
    preview_disable('profession')
    preview_disable('file')
    preview_disable('checkbox')
    preview_disable('submit')
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


function appendElement(bullets, bullet_id) {

    var bullet = document.getElementById(bullet_id);

    var element = document.createElement("li");
    element.name = bullet.value;
    element.value = bullet.value;
    element.id = bullet.id;
    bullets.appendChild(element);
}


function editPreviewBullets(bullet_id) {
    copyText(bullet_id, bullet_id);
}
