function getIframeDocs(){
    var frames = document.getElementsByClassName('preview')
    return [frames[0].contentWindow.document, frames[1].contentWindow.document]
}


function getContainerId(type) {
    return type + '-container';
}


function getTitleDiv(type, iframe_doc){
    return iframe_doc.getElementById(type + "-title-div");
}


function getTitleId(type){
    return type + '-title-id';
}


/*
Copies text from a Source element to a target element.
*/
function copyText(source, target) {

    var my_iframe_docs = getIframeDocs();
    var source_text = document.getElementById(source).value;

    my_iframe_docs[0].getElementById(target).innerHTML = source_text;
    my_iframe_docs[1].getElementById(target).innerHTML = source_text;
}
