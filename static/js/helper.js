function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

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

function formEventCapture(id) {
    $(document).ready(function() {
        $(id).submit(function() { // catch the form's submit event
            $.ajax({ // create an AJAX call...
                data: $(this).serialize(), // get the form data
                type: $(this).attr('method'), // GET or POST
                url: $(this).attr('action'), // the file to call
                success: function(response) { // on success..
                    if (response.Retcode == 0) $(id).hide();
                    else alert('Invalid Form')
                },
                error: function(e, x, r) { // on error..
                    alert(e)
                }
            });
            return false;
        });
    });
}