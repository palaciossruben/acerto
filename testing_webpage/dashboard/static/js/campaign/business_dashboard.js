function count_candidates() {
    var div = document.getElementById("backlog");
    var candidate_list = div.getElementsByTagName("li");
    document.getElementById("quantity_backlog").innerHTML = candidate_list.length;

    var div = document.getElementById("waiting_test");
    var candidate_list = div.getElementsByTagName("li");
    document.getElementById("quantity_waiting_test").innerHTML = candidate_list.length;

    var div = document.getElementById("waiting_interview");
    var candidate_list = div.getElementsByTagName("li");
    document.getElementById("quantity_waiting_interview").innerHTML = candidate_list.length;

    var div = document.getElementById("did_interview");
    var candidate_list = div.getElementsByTagName("li");
    document.getElementById("quantity_did_interview").innerHTML = candidate_list.length;

    var div = document.getElementById("send_to_client");
    var candidate_list = div.getElementsByTagName("li");
    document.getElementById("quantity_send_to_client").innerHTML = candidate_list.length;

    var div = document.getElementById("got_job");
    var candidate_list = div.getElementsByTagName("li");
    document.getElementById("quantity_got_job").innerHTML = candidate_list.length;

    var div = document.getElementById("rejected");
    var candidate_list = div.getElementsByTagName("li");
    document.getElementById("quantity_rejected").innerHTML = candidate_list.length;
}