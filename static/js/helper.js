function formatRediectUrl(source, replace, target) {
    var redirect_url = source.replace(replace, target);
    console.log(redirect_url);
    return redirect_url;
}

function urlLastSegment(url) {
    var parts = url.split('/');
    var lastSegment = parts.pop() || parts.pop();  // handle potential trailing slash
    console.log(lastSegment);
    return lastSegment;
}