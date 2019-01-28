options = {
    sanitize: true
}

function makeMarked(id) {
    var elem = document.getElementById(id);
    elem.innerHTML = marked(elem.innerHTML.replace(/&gt;/g, '>'), options);
}