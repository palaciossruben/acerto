function set_background(image_name, id_string){

    image_name = image_name.replace("&#39;","");
    console.log(image_name);
    if (image_name == 'default'){
        image_name = "Start_BG-01-min.jpg);"
    }
    console.log(image_name);
    var me = document.getElementById(id_string);
    if(me == null){
    }else{
        var url = 'url(../static/beta_invite/img/' + image_name;
        me.style["background-image"] = url;
        me.style["background-size"] = "contain";
        me.style["background-repeat"] = "no-repeat";
        console.log(url);
    }
}
