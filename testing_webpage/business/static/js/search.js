function TurnOffAdblockAlert(){
    /*
    Displays message in case Adblock is turned on. Telling the user to turn it of before continuing.
    */

    console.log("inside adblock")

    var adBlockEnabled = false;
    var testAd = document.createElement('div');
    testAd.innerHTML = '&nbsp;';
    testAd.className = 'adsbox';
    document.body.appendChild(testAd);
    window.setTimeout(function() {
      if (testAd.offsetHeight === 0) {
        adBlockEnabled = true;
      }
      testAd.remove();
      console.log('AdBlock Enabledd? ', adBlockEnabled)

      if (adBlockEnabled === true) {

        var language = window.navigator.userLanguage || window.navigator.language; //works IE/SAFARI/CHROME/FF

        if (language == 'es'){
            alert("Por favor apaga Adblock para que está webapp funcione correctamente.")
        } else {
            alert("Make sure you have Adblocker turned off for this app to work correctly.")
        }
      }
    }, 100);
}


function SetSignUpModal(is_authenticated, action_url){
    /*
    Sets up a modal to register a new user after exceeding 3 searches on the same browser.
    */
    console.log("started SetSignUpModel")
    var search_form = $('#search_form')[0];

    if (is_authenticated) {
        search_form.action = action_url;
    } else {

        console.log("not authenticated")

        if(typeof(Storage) !== "undefined") {

            console.log("Valid storage")

            if (localStorage.clickcount) {
                localStorage.clickcount = Number(localStorage.clickcount)+1;
            } else {
                localStorage.clickcount = 1;
            }

            if ( Number(localStorage.clickcount) > 3 ) {

                console.log("more than 3 clicks")

                var modal = $('#search_modal')[0];
                var span = document.getElementsByClassName("close")[0];

                TurnOffAdblockAlert()

                //Display modal
                //modal.style.display = "block";

                // When the user clicks on <span> (x), close the modal
                span.onclick = function() {
                    modal.style.display = "none";
                }

                // When the user clicks anywhere outside of the modal, close it
                window.onclick = function(event) {
                    if (event.target == modal) {
                        modal.style.display = "none";
                    }
                }

                // Stays on the page, with a opened modal
                search_form.action = '#';

            } else {
                search_form.action = action_url;
            }

        } else {
            search_form.action = action_url;
        }
    }
}
