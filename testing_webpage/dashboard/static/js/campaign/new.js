var bullet_number = 1;

function addBulletTypeSelector(container, bullet_types) {

    var bullet_type = document.createElement("select");
    bullet_type.name = bullet_number + "_new_bullet_type";
    bullet_type.required = true;
    container.appendChild(bullet_type);

    //Create and append the options
    var option = document.createElement("option");
    option.value = "";
    option.text = "Select an option";
    bullet_type.appendChild(option);

    for (var i = 0; i < bullet_types.length; i++) {
        var option = document.createElement("option");
        option.value = bullet_types[i].pk;
        option.text = bullet_types[i].fields.name;
        bullet_type.appendChild(option);
    }
}

function build_text_field(container, name, placeholder) {

    var text_input = document.createElement("input");
    text_input.type = "text";
    text_input.style.width = "500px"
    text_input.name = name;
    text_input.placeholder = placeholder;
    container.appendChild(text_input);
}

function addBullet(bullet_types){
    /*
    Adds a bullet to the interface and numbers it.
    */
    bullet_types = JSON.parse(bullet_types)

    var container = document.getElementById("bullet_container");
    container.appendChild(document.createElement("br"));
    container.appendChild(document.createTextNode("Bullet " + bullet_number));

    container.appendChild(document.createElement("br"));

    build_text_field(container, bullet_number + "_new_bullet_name", "add text in english")

    container.appendChild(document.createElement("br"));

    build_text_field(container, bullet_number + "_new_bullet_name_es", "add text in spanish")

    container.appendChild(document.createElement("br"));

    addBulletTypeSelector(container, bullet_types)

    var remove_button = document.createElement("input");
    remove_button.type = "button";
    remove_button.class = "btn btn-danger"
    remove_button.value = "Delete!"
    remove_button.onclick = "deleteBullet(" + bullet_number + ")"
    container.appendChild(remove_button);

    container.appendChild(remove_button);
    container.appendChild(document.createElement("br"));
    container.appendChild(document.createElement("br"));

    //adds 1 for next bullet.
    bullet_number = bullet_number + 1
}
