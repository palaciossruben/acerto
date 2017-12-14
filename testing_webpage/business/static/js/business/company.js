var bullet_number2 = 1;

function build_text_field2(div, name, placeholder) {

    var text_input = document.createElement("input");
    text_input.type = "text";
    text_input.size = "100";
    text_input.name = name;
    text_input.placeholder = placeholder;
    div.appendChild(text_input);
}

function build_bullet_ui2(container) {

    var div = document.createElement("div")

    container.appendChild(div);

    div.appendChild(document.createElement("br"));

    div.appendChild(document.createTextNode("Beneficio " + bullet_number2));

    div.appendChild(document.createElement("br"));

    build_text_field2(div, bullet_number2 + "_new_bullet_name", "Ingresa un beneficio");

    div.appendChild(document.createElement("br"));

    div.appendChild(document.createElement("br"));

}

function addBullet2(){
    /*
    Adds a bullet to the interface and numbers it.
    */
    var container = document.getElementById("bullet_container2");

    build_bullet_ui2(container);

    //adds 1 for next bullet.
    bullet_number2 = bullet_number2 + 1
}

function removeBullet2(){
    /*
    Delete a bullet to the interface
    */
    var container = document.getElementById("bullet_container2");

    container.removeChild(container.lastChild);

    bullet_number2 = bullet_number2 -1
}