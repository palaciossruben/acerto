var cont = 0;

function count_candidates() {
    var div = document.getElementById("backlog");
    var candidate_list = div.getElementsByTagName("li");
    document.getElementById("quantity").innerHTML = candidate_list.length;
}