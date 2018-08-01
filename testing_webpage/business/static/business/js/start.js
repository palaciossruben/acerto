function get_background(background){
    var elem = document.getElementById("test");
    var image_url = window.getComputedStyle(elem, null).getPropertyValue("background-image").replace('url("http://peaku.co/static/business/img/', '');
    var image_url_final = image_url.replace('")',')');
    document.getElementById("demo").value = image_url_final;
}