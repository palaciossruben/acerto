function activate_tab(tab_id){
    document.getElementById(tab_id).style.display = "block";
}

function tab(tab_active, step_name) {

    var i, tab_content, tab_links;
    tab_content = document.getElementsByClassName("tab-content");

    for (i = 0; i < tab_content.length; i++) {
        tab_content[i].style.display = "none";
    }

    tab_links = document.getElementsByClassName("tab-links");

    for (i = 0; i < tab_links.length; i++) {
        tab_links[i].className = tab_links[i].className.replace(" active", "");
    }

    document.getElementById(step_name).style.display = "block";
    tab_active.currentTarget.className += " active";
}
