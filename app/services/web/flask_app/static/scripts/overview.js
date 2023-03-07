/*const picker = new easepick.create({
    element: "#author",
    css: [
        "https://cdn.jsdelivr.net/npm/@easepick/bundle@1.2.0/dist/index.css"
    ],
    zIndex: 10,
    plugins: [
        "RangePlugin"
    ]
})*/

const MONTHS = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December'
];

function months(config) {
    var cfg = config || {};
    var count = cfg.count || 12;
    var section = cfg.section;
    var values = [];
    var i, value;

    for (i = 0; i < count; ++i) {
        value = MONTHS[Math.ceil(i) % 12];
        values.push(value.substring(0, section));
    }

    return values;
}

const COLORS = [
    '#000',
    '#000',
];

function color(index) {
    return COLORS[index % COLORS.length];
}

function transparentize(value, opacity) {
    var alpha = opacity === undefined ? 0.5 : 1 - opacity;
    return colorLib(value).alpha(alpha).rgbString();
}

const CHART_COLORS = {
    red: 'rgb(255, 99, 132)',
    orange: 'rgb(255, 159, 64)',
    yellow: 'rgb(255, 205, 86)',
    green: 'rgb(75, 192, 192)',
    blue: 'rgb(54, 162, 235)',
    purple: 'rgb(153, 102, 255)',
    grey: 'rgb(201, 203, 207)'
};

const NAMED_COLORS = [
    CHART_COLORS.red,
    CHART_COLORS.orange,
    CHART_COLORS.yellow,
    CHART_COLORS.green,
    CHART_COLORS.blue,
    CHART_COLORS.purple,
    CHART_COLORS.grey,
];

function namedColor(index) {
    return NAMED_COLORS[index % NAMED_COLORS.length];
}

function newDate(days) {
    return DateTime.now().plus({ days }).toJSDate();
}

function newDateString(days) {
    return DateTime.now().plus({ days }).toISO();
}

function parseISODate(str) {
    return DateTime.fromISO(str);
}
const ctx = document.getElementById('myChart').getContext('2d');
const myChart = new Chart(ctx,{type: 'line'});
function build_chart(chart_data) {
    const labels = chart_data['labels'];
    var data = {
        labels: labels,
        datasets: []
    };
    Object.entries(chart_data['data']).forEach(([key, value], index) => {
        data['datasets'].push({
            label: key,
            data: value,
            fill: false,
            borderColor: COLORS[index],
            tension: 0.0,
            pointRadius: 0
        })
        });
    myChart.data = data;
    myChart.update();
    document.getElementById('loader').style.visibility = "hidden";
}

function handle_response(response) {

    if ('message' in response) {
        throw new Error(response['message']);
    }
    else {
        return response
    }
}

search_url = '/analysis/company-fact';
obj_view_endpoint = '/plant/view/';
no_results_html = '<br>No results found';

function set_chart_listeners(){
    const chart_links = document.querySelectorAll('.ticker-chart-link');
    chart_links.forEach(el => el.addEventListener('click', event => {
        console.log(event.target.getAttribute("data-el"))
        populate_analysis_chart(event.target.getAttribute("data-el"));
        }));
}


document.getElementById('query_button').addEventListener('click', function () {
    search_list = new SearchList(search_url, obj_view_endpoint, no_results_html,1,set_chart_listeners);
    
    search_list.do_search(
        document.getElementById("analysis_label").value,
        document.getElementById("indicator").value);
    
console.log('done');
}, false);





function show_error(error_msg) {
    document.getElementById('warner').innerHTML = error_msg;
    document.getElementById('warner').style.visibility = "visible";
    document.getElementById('loader').style.visibility = "hidden";
}

function populate_chart(title, author) {

    if (title != null) {
        document.getElementById('title').value = title;
    }

    document.getElementById('warner').style.visibility = "hidden";
    title = get_input_value('title');
    author = get_input_value('author');

    if (author === '' && title === '') {
        document.getElementById('warner').style.visibility = "visible";
    } else {
        document.getElementById('loader').style.visibility = "visible";
        params = {
            'title': title,
            'author': author
        };
        do_get('/get-quote', params)
            .then(content => handle_response(content))
            .then(content => build_chart(content))
            .catch(reason => show_error(reason));
    }
}


function populate_analysis_chart(ticker) {

    //document.getElementById('warner').style.visibility = "hidden";
    analysis_label = document.getElementById("analysis_label").value;
    indicator = document.getElementById("indicator").value;

   
    document.getElementById('loader').style.visibility = "visible";
    params = {
        'analysis_label': analysis_label,
        'ticker': ticker,
        'indicator': indicator
    };
    do_get('/company-fact-chart', params)
        .then(content => handle_response(content))
        .then(content => build_chart(content))
        .catch(reason => show_error(reason));
    
}