//we wait for page load to be finished (you could use jQuery ready event as well, or any such alternative that you prefer)
ZiggeoApi.Events.on("system_ready", function() {
    //Lets get the ziggeo-recorder element reference
    var element = document.getElementById('myRecorder');

    //now lets get the actual Ziggeo embedding / object that we can use
    var recorder = ZiggeoApi.V2.Recorder.findByElement(element);

    // we can also create a global event to fire each time video was uploaded
    recorder.on("verified", function () {

        form = document.getElementById('right_button_form_id');
        video_token = document.createElement('input');
        video_token.setAttribute('name', 'new_video_token');
        video_token.setAttribute('type', 'hidden');
        video_token.setAttribute('value', recorder.get('video'));
        form.appendChild(video_token);

        //enables save button
        document.getElementById("right_button_id").disabled = false;
    });
});

function disable_continue_button_on_interview(needs_to_record){
    if (needs_to_record){
        document.getElementById("right_button_id").disabled = true;
    }
}
