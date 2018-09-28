function set_background(image_name, id_string){

    image_name = image_name.replace("&#39;","");
    if (image_name == 'default' || image_name == ''){
        image_name = "Start_BG-07.jpg)"
    }

    if ($(window).width() < 768) {
        image_name = 'cel-' + image_name;
    }

    var me = document.getElementById(id_string);
    if(me == null){
    }else{
        var url = 'url(../static/beta_invite/img/' + image_name;
        me.style["background-image"] = url;
    }
}