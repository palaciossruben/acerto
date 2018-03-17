var bullet_types = {"perk":1, "requirement":2};
var bullet_numbers = {"perk":2, "requirement":2};
var unique_bullet_number = 3;


function build_text_field(div, name, placeholder, type) {

    var text_input = document.createElement("input");
    text_input.type = "text";
    text_input.classList.add('box-input');
    text_input.name = name;
    text_input.placeholder = placeholder;
    text_input.addEventListener('input', function() { editPreviewBullets(this.id); } );
    text_input.id = getBulletId(bullet_numbers, type);
    div.appendChild(text_input);
}


function add_hidden_bullet_type(div, bullet_type_id){

    var bullet_type = document.createElement("input");
    bullet_type.name = unique_bullet_number + "_new_bullet_type";
    bullet_type.type = "hidden"
    bullet_type.value = bullet_type_id;
    div.appendChild(bullet_type);
}


function build_bullet_ui(container, type, bullet_text, add_bullet_text) {

    var div = document.createElement("div")

    container.appendChild(div);

    div.appendChild(document.createElement("br"));
    div.appendChild(document.createElement("br"));

    //TODO: compatibility with other languages.
    build_text_field(div, unique_bullet_number + "_new_bullet_name_es", add_bullet_text, type);

    add_hidden_bullet_type(div, bullet_types[type]);

    div.appendChild(document.createElement("br"));
}


/*
Adds one bullet to a given Iframe
*/
function addBulletOnIframeType(bullet_numbers, type, iframe, text1, text2){

    // Adds Title if not present
    addBulletTitle(type, text1, text2);

    var list_id = getListId(type);
    var bullet_id = getBulletId(bullet_numbers, type);
    var bullets = getListItems(list_id, type, iframe + '_iframe');

    appendElement(bullets, bullet_id);
}


function addBulletOnIframe(bullet_numbers, iframe, text1, text2){
    addBulletOnIframeType(bullet_numbers, 'requirement', iframe, text1, text2);
    addBulletOnIframeType(bullet_numbers, 'perk', iframe, text1, text2);
}


/*
Adds one bullet to both iframes
*/
function addBulletOnIframes(bullet_numbers, type, text1, text2){
    addBulletOnIframeType(bullet_numbers, type, 'vacancy', text1, text2);
    addBulletOnIframeType(bullet_numbers, type, 'company', text1, text2);
}

/*
Adds a bullet to the interface and numbers it.
*/
function addBullet(type, bullet_text, add_bullet_text){

    var container = document.getElementById(getContainerId(type));

    build_bullet_ui(container, type, bullet_text, add_bullet_text);

    addBulletOnIframes(bullet_numbers, type);

    //adds 1 for next bullet.
    bullet_numbers[type] = bullet_numbers[type] + 1
    unique_bullet_number = unique_bullet_number + 1
}


function addBulletTitle(type, text1, text2){
    var iframe_docs = getIframeDocs();

    // if there is no title yet.
    if (!iframe_docs[0].getElementById(getTitleId(type))) {
        addsBulletTitleToIframe(type, iframe_docs[0], text1, text2);
        addsBulletTitleToIframe(type, iframe_docs[1], text1, text2);
    }
}


/*
Adds the title if missing.
*/
function addsBulletTitleToIframe(type, iframe_doc, text1, text2){

    var title_div = getTitleDiv(type, iframe_doc);

    var bullet_title = document.createElement("h4");
    bullet_title.classList.add('title-blue');
    bullet_title.align = "left";
    bullet_title.id = getTitleId(type);

    //TODO: missing translation
    if (type == 'requirement'){
        text = text1;
    }else{
        text = text2;
    }
    bullet_title.appendChild(iframe_doc.createTextNode(text));

    title_div.appendChild(bullet_title);
}


/*
Removes last element from iframe_container
*/
function removeOnPreview(iframe_container, iframe_doc){
    var container = iframe_doc.getElementById(iframe_container);
    container.removeChild(container.lastChild);
}


/*
Delete a bullet to the interface. Assumes that bullet ids are always ordered in ASC, on the table. It removes
the last one, therefore It should ALWAYS remove the one biggest id.
*/
function removeBullet(type){

    var iframe_container = type + '-bullets-list';
    var container_name = getContainerId(type);

    // Removes in native container
    var container = document.getElementById(container_name);

    if (bullet_numbers[type] > 2){
        container.removeChild(container.lastChild);
        bullet_numbers[type] = bullet_numbers[type] - 1;
        unique_bullet_number = unique_bullet_number - 1;

        // Removes on both previews.
        var iframe_docs = getIframeDocs();
        removeOnPreview(iframe_container, iframe_docs[0]);
        removeOnPreview(iframe_container, iframe_docs[1]);
    }
}
