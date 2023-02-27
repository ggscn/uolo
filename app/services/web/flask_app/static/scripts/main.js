function url_encode_dict(params){
    let data = Object.entries(params);

    data = data.map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`);

    let query = data.join('&');

    return query
}

async function do_get(url, params={}) {
    const csrfToken = $('meta[name=csrf-token]').attr('content');

    if (!(Object.entries(params).length === 0 && params.constructor === Object)){
        url_encoded_params = url_encode_dict(params);
        url = url + '?' + url_encoded_params;
    }
    
    let response = await fetch(url, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    });
    if (!response.ok) {
        throw Error(response.statusText);
    }
    

    let content = await response.json();

    return content;
}


function get_input_value(ele_id){
    return document.getElementById(ele_id).value;
}

