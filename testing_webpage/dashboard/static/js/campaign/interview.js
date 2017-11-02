//we wait for page load to be finished (you could use jQuery ready event as well, or any such alternative that you prefer)
ZiggeoApi.Events.on("system_ready", function() {
    //Lets get the ziggeo-recorder element reference
    var element = document.getElementById('myRecorder');

    //now lets get the actual Ziggeo embedding / object that we can use
    var recorder = ZiggeoApi.V2.Recorder.findByElement(element);

    // we can also create a global event to fire each time video was uploaded
    recorder.on("verified", function () {
        alert("The video with token '" + recorder.get('video') + "' has been submitted!");

        form = document.getElementById('main_form_id');

        video_token = document.createElement('input');
        video_token.setAttribute('name', 'new_video_token');
        video_token.setAttribute('type', 'hidden');
        video_token.setAttribute('value', recorder.get('video'));
        form.appendChild(video_token);
    });
});


function submit_form() {
    form = document.getElementById('main_form_id');
    form.submit();
}
