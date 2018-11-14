function get_background(){
    var elem = document.getElementById("test");
    // This replace regex works for debug and production
    var image_url = window.getComputedStyle(elem, null).getPropertyValue("background-image").replace(/^.+img\//g,'');

    var image_url_final = image_url.replace('")',')');
    document.getElementById("demo").value = image_url_final;
}

function dynamic_select_values(work_area_json_url){
    $("#first-choice").change(function() {
    var $dropdown = $(this);

    $.getJSON(work_area_json_url, function(data) {

        var key = $dropdown.val();
        var $secondChoice = $("#second-choice");
        $secondChoice.empty();
        $.each(JSON.parse(data), function(index, value) {
           $secondChoice.append("<option value=" + value.pk + ">" + value.name + "</option>");
        });
    });
});
}