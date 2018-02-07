function count_candidates_in_a_column(column_name){
    /* Changes the UI to reflect counting the number of items in a column */
    var div = document.getElementById(column_name);
    var candidate_list = div.getElementsByTagName("li");
    document.getElementById("quantity_" + column_name).innerHTML = candidate_list.length;
}


function count_candidates() {
    /* Counts items in all columns */

    states = ["backlog",
              "waiting_interview",
              "did_interview",
              "sent_to_client",
              "got_job",
              "rejected"]

    for (i = 0; i < states.length; i++)  {
        count_candidates_in_a_column(states[i])
    }
}
