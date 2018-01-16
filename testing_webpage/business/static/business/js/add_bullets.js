var bullet_types = {"perk":1, "requirement":2};
var bullet_numbers = {"perk":2, "requirement":2};


function build_text_field(div, name, placeholder, type) {

    var text_input = document.createElement("input");
    text_input.type = "text";
    text_input.classList.add('box-input');
    text_input.name = name;
    text_input.placeholder = placeholder;
    text_input.addEventListener('input', function() { editPreviewBullets(this.id); } );
    text_input.id = bullet_numbers[type] + "_" + type;
    div.appendChild(text_input);
}


function add_hidden_bullet_type(div, bullet_type_id, bullet_number){

    var bullet_type = document.createElement("input");
    bullet_type.name = bullet_number + "_new_bullet_type";
    bullet_type.type = "hidden"
    bullet_type.value = bullet_type_id;
    div.appendChild(bullet_type);
}


function build_bullet_ui(container, type, bullet_text, add_bullet_text) {

    var div = document.createElement("div")

    container.appendChild(div);

    div.appendChild(document.createElement("br"));
    div.appendChild(document.createElement("br"));

    build_text_field(div, bullet_numbers[type] + "_new_bullet_name_" + type, add_bullet_text, type);

    add_hidden_bullet_type(div, bullet_types[type], bullet_numbers[type]);

    div.appendChild(document.createElement("br"));
}


/*
Adds a bullet to the interface and numbers it.
*/
function addBullet(type, bullet_text, add_bullet_text){

    var container = document.getElementById(getContainerId(type));

    build_bullet_ui(container, type, bullet_text, add_bullet_text);

    addBulletTitle(type);

    //adds 1 for next bullet.
    bullet_numbers[type] = bullet_numbers[type] + 1
}


function addBulletTitle(type){
    var iframe_docs = getIframeDocs();

    // if there is no title yet.
    if (!iframe_docs[0].getElementById(getTitleId(type))) {
        addsBulletTitleToIframe(type, iframe_docs[0]);
        addsBulletTitleToIframe(type, iframe_docs[1]);
    }
}


/*
Adds the title if missing.
*/
function addsBulletTitleToIframe(type, iframe_doc){

    var title_div = getTitleDiv(type, iframe_doc);

    var bullet_title = document.createElement("h4");
    bullet_title.classList.add('title-blue');
    bullet_title.align = "left";
    bullet_title.id = getTitleId(type);

    //TODO: missing translation
    if (type == 'requirement'){
        text = "Requerimientos";
    }else{
        text = "Beneficios";
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


function removeTitle(type, iframe_doc){
    var title_div = getTitleDiv(type, iframe_doc);
    title_div.removeChild(title_div.lastChild);
}


/*
Delete a bullet to the interface
*/
function removeBullet(type){

    var iframe_container = type + '-bullets-list';
    var container_name = getContainerId(type);

    // Removes in native container
    var container = document.getElementById(container_name);
    container.removeChild(container.lastChild);
    bullet_numbers[type] = bullet_numbers[type] - 1

    // Removes on both previews.
    var iframe_docs = getIframeDocs();
    removeOnPreview(iframe_container, iframe_docs[0])
    removeOnPreview(iframe_container, iframe_docs[1])

    // Checks to remove if no elements present.
    if(!countItems(getListId(type))){
        removeTitle(type, iframe_docs[0]);
        removeTitle(type, iframe_docs[1]);
    }
}
