var stamenLayer = new ol.layer.Tile({
    source: new ol.source.Stamen({
      layer: 'toner-lite'
    })
  });


var flask_app = new ol.Map({
    target: 'map',
    layers: [
        stamenLayer
    ],
    view: new ol.View({
        center: ol.proj.fromLonLat([28.41, 50.82]),
        zoom: 4
    }),
    interactions: ol.interaction.defaults({
        doubleClickZoom: true,
        dragAndDrop: true,
        dragPan: true,
        keyboardPan: true,
        keyboardZoom: true,
        mouseWheelZoom: true,
        pointer: true,
        select: true
    }),
});




function draw_markers(rows) {

    flask_app.getLayers().forEach(layer => {
        console.log(layer.get('name'));
        if (layer && layer.get('name') === 'markers') {
          flask_app.removeLayer(layer);
        }
    });

    var features = [];

    for (var i = 0; i < rows.length; i++) {
        var item = rows[i];
        var longitude = item.long;
        var latitude = item.lat;
        var cnt = item.cnt;

        var iconFeature = new ol.Feature({
            geometry: new ol.geom.Point(ol.proj.transform([longitude, latitude], 'EPSG:4326', 'EPSG:3857'))
        });

        var iconStyle = new ol.style.Style({
            image: new ol.style.Icon(({
                anchor: [0.5, 1],
                src: "https://cdn.mapmarker.io/api/v1/pin?text=" + cnt + "&color=%23fff&size=50&hoffset=1&background=%23000"
            }))
        });

        iconFeature.setStyle(iconStyle);
        features.push(iconFeature);

    }

    var vectorSource = new ol.source.Vector({
        features: features
    });

    var vectorLayer = new ol.layer.Vector({
        source: vectorSource
    });
    vectorLayer.set('name', 'markers')
    flask_app.addLayer(vectorLayer);
    document.getElementById('loader').style.visibility = "hidden";
}

function show_error(error_msg){
    document.getElementById('warner').innerHTML = error_msg;
    document.getElementById('warner').style.visibility = "visible";
    document.getElementById('loader').style.visibility = "hidden";
}

function handle_response(response){

    if ('message' in response){
        throw new Error(response['message']);
    }
    else { 
        return response
    }
}

function populate_map(title, author) {

    if (title != null && author != null){
        document.getElementById('title').value = title;
        document.getElementById('author').value = author;
    }

    document.getElementById('warner').style.visibility = "hidden";
    author = get_input_value('author');
    title = get_input_value('title');

    if (author === '' && title === ''){
        document.getElementById('warner').style.visibility = "visible";
    } else {
        document.getElementById('loader').style.visibility = "visible";
        params = {
            'title': title,
            'author': author
        };
        do_get('/query', params)
            .then(content => handle_response(content))
            .then(content => draw_markers(content['data']))
            .catch(reason => show_error(reason));
    }
}



document.getElementById('query_button').addEventListener('click', function () {
    
    populate_map(null);
    
}, false);

document.getElementById('helper-1').addEventListener('click', function () {
    
    populate_map('The Whale', 'Melville');
    
}, false);



document.getElementById('author').addEventListener('onkeydown', function (e) {
    console.log('test');
    var key = e.which || e.keyCode || 0;
    if (key == 13) {
        populate_map(null);
    }
});

