function SetSignUpModal(is_authenticated, action_url){

    var search_form = $('#search_form')[0];

    if (is_authenticated) {
        search_form.action = action_url;
    } else {

        if(typeof(Storage) !== "undefined") {

            if (localStorage.clickcount) {
                localStorage.clickcount = Number(localStorage.clickcount)+1;
            } else {
                localStorage.clickcount = 1;
            }

            if ( Number(localStorage.clickcount) > 3 ) {

                var modal = $('#search_modal')[0];
                var span = document.getElementsByClassName("close")[0];

                //Display modal
                modal.style.display = "block";

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
