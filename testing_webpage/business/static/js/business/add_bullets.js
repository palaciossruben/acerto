var bullet_number = 3;

function build_text_field(div, name, placeholder) {

    var text_input = document.createElement("input");
    text_input.type = "text";
    text_input.size = "80";
    text_input.name = name;
    text_input.placeholder = placeholder;
    div.appendChild(text_input);
}


function add_hidden_bullet_type(div, bullet_type_id){

    var bullet_type = document.createElement("input");
    bullet_type.name = bullet_number + "_new_bullet_type";
    bullet_type.type = "hidden"
    bullet_type.value = bullet_type_id;
    div.appendChild(bullet_type);
}


function build_bullet_ui(container, bullet_type_id, bullet_text, add_bullet_text) {

    var div = document.createElement("div")

    container.appendChild(div);

    div.appendChild(document.createElement("br"));

    //div.appendChild(document.createTextNode(bullet_text + " " + bullet_number));

    div.appendChild(document.createElement("br"));

    build_text_field(div, bullet_number + "_new_bullet_name", add_bullet_text);

    add_hidden_bullet_type(div, bullet_type_id);

    div.appendChild(document.createElement("br"));


}

function addBullet(bullet_type_id, container_name, bullet_text, add_bullet_text){
    /*
    Adds a bullet to the interface and numbers it.
    */
    var container = document.getElementById(container_name);

    build_bullet_ui(container, bullet_type_id, bullet_text, add_bullet_text);

    //adds 1 for next bullet.
    bullet_number = bullet_number + 1
}

function removeBullet(container_name){
    /*
    Delete a bullet to the interface
    */
    var container = document.getElementById(container_name);

    container.removeChild(container.lastChild);

    bullet_number = bullet_number - 1
}
