var bullet_number = 1;

function build_text_field(div, name, placeholder) {

    var text_input = document.createElement("input");
    text_input.type = "text";
    text_input.size = "100";
    text_input.name = name;
    text_input.placeholder = placeholder;
    div.appendChild(text_input);
}

function build_bullet_ui(container) {

    var div = document.createElement("div")

    container.appendChild(div);

    div.appendChild(document.createElement("br"));

    div.appendChild(document.createTextNode("Requerimiento " + bullet_number));

    div.appendChild(document.createElement("br"));

    build_text_field(div, bullet_number + "_new_bullet_name", "Ingresa un requerimiento");

    div.appendChild(document.createElement("br"));

    div.appendChild(document.createElement("br"));

}

function addBullet(){
    /*
    Adds a bullet to the interface and numbers it.
    */
    var container = document.getElementById("bullet_container");

    build_bullet_ui(container);

    //adds 1 for next bullet.
    bullet_number = bullet_number + 1
}

function removeBullet(){
    /*
    Delete a bullet to the interface
    */
    var container = document.getElementById("bullet_container");

    container.removeChild(container.lastChild);

    bullet_number = bullet_number -1
}