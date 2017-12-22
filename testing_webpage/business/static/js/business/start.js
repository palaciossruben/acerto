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

    //Show tab content
    var next_content = document.getElementById(step_name)
    next_content.style.display = "block";

    tab_active.currentTarget.className += " active";
}

function next_step_tab(tab_active, step_name){

    tab(tab_active, step_name)

    //Enable tab button and mark the tab, avoid double mark
    var next_button = document.getElementById(step_name + "_button")
    next_button.disabled = false;
    next_button.className += " active";
}
