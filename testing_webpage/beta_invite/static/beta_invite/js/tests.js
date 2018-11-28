function activate(test_number, question_number){
    $('#container-'+test_number+'-'+question_number).css({'display': 'block'});
}

function deactivate(test_number, question_number){
    $('#container-'+test_number+'-'+question_number).css({'display': 'none'});
}

function back(test_number, question_number, last_test_number_of_questions){
    if (question_number == 1) {
        activate(test_number -1, last_test_number_of_questions);
    }else{
        activate(test_number, question_number - 1);
    }
    deactivate(test_number, question_number);
}

function next(test_number, question_number, number_of_questions, number_of_tests){

    if (question_number == number_of_questions) {
        activate(test_number +1, 1);
    }else{
        activate(test_number, question_number + 1);
    }

    if (test_number == number_of_tests && question_number == number_of_questions - 1){
        $('#submit-button').css({'display': 'block'});
    }
    deactivate(test_number, question_number);
}


function timer(){
    var minutesLabel = document.getElementById("minutes");
    var secondsLabel = document.getElementById("seconds");
    var totalSeconds = 0;
    setInterval(setTime, 1000);

    function setTime() {
        ++totalSeconds;
        secondsLabel.innerHTML = pad(totalSeconds % 60);
        minutesLabel.innerHTML = pad(parseInt(totalSeconds / 60));
    }

    function pad(val) {
        var valString = val + "";
        if (valString.length < 2) {
            return "0" + valString;
        } else {
            return valString;
        }
    }
}


function startRecording() {
    console.log("recordButton clicked");

    /*
    Simple constraints object, for more advanced audio features see
    <div class="video-container"><blockquote class="wp-embedded-content" data-secret="cVHlrYJoGD"><a href="https://addpipe.com/blog/audio-constraints-getusermedia/">Supported Audio Constraints in getUserMedia()</a></blockquote><iframe class="wp-embedded-content" sandbox="allow-scripts" security="restricted" style="position: absolute; clip: rect(1px, 1px, 1px, 1px);" src="https://addpipe.com/blog/audio-constraints-getusermedia/embed/#?secret=cVHlrYJoGD" data-secret="cVHlrYJoGD" width="600" height="338" title="“Supported Audio Constraints in getUserMedia()” — Pipe Blog" frameborder="0" marginwidth="0" marginheight="0" scrolling="no"></iframe></div>
    */

    var constraints = { audio: true, video:false }

    /*
    Disable the record button until we get a success or fail from getUserMedia()
    */

    recordButton.disabled = true;
    stopButton.disabled = false;

    /*
    We're using the standard promise based getUserMedia()
    https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
    */

    navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
        console.log("getUserMedia() success, stream created, initializing Recorder.js ...");

        /* assign to gumStream for later use */
        gumStream = stream;

        /* use the stream */
        input = audioContext.createMediaStreamSource(stream);

        /*
        Create the Recorder object and configure to record mono sound (1 channel)
        Recording 2 channels  will double the file size
        */
        rec = new Recorder(input,{numChannels:1})

        //start the recording process
        rec.record()

        console.log("Recording started");

    }).catch(function(err) {
        //enable the record button if getUserMedia() fails
        recordButton.disabled = false;
        stopButton.disabled = true;
    });
}

function stopRecording() {
    console.log("stopButton clicked");

    //disable the stop button, enable the record too allow for new recordings
    stopButton.disabled = true;
    recordButton.disabled = false;

    //tell the recorder to stop the recording
    rec.stop();

    //stop microphone access
    gumStream.getAudioTracks()[0].stop();

    //create the wav blob and pass it on to createDownloadLink
    rec.exportWAV(createDownloadLink);
}


function createDownloadLink(blob) {

    var url = URL.createObjectURL(blob);
    var au = document.createElement('audio');
    var li = document.createElement('li');
    var link = document.createElement('a');

    //add controls to the <audio> element
    au.controls = true;
    au.src = url;

    //link the a element to the blob
    link.href = url;
    link.download = 'audio_file.wav';
    link.innerHTML = link.download;

    //add the new audio and a elements to the li element
    li.appendChild(au);
    li.appendChild(link);

    //add the li element to the ordered list
    recordingsList.appendChild(li);


    var formElement = document.getElementById("test_form_id");

    var formData = new FormData(formElement);
    formData.append('audio_file.wav', blob, 'audio_file.wav');

    var fd = new FormData();
    fd.append('audio', blob);

    //TODO: These can not be hardcoded!
    /*
    fd.append('question_id', 1682);
    fd.append('campaign_id', 464);
    fd.append('test_id', 357);
*/
    fd.append('question_id', 444);
    fd.append('campaign_id', 22);
    fd.append('test_id', 109);

    $.ajax({
        type: 'POST',
        url: /*'https://peaku.co/servicio_de_empleo/upload-audio-file',  */ 'http://127.0.0.1:8000/servicio_de_empleo/upload-audio-file',
        data: fd,
        processData: false,
        contentType: false
    }).done(function(data) {
           console.log(data);
    });
}

//webkitURL is deprecated but nevertheless
URL = window.URL || window.webkitURL;

var gumStream; //stream from getUserMedia()
var rec; //Recorder.js object
var input; //MediaStreamAudioSourceNode we'll be recording

// shim for AudioContext when it's not avb.
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext = new AudioContext; //new audio context to help us record

var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");

//add events to those 3 buttons
recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);
