class SearchList {
    constructor(search_url, obj_endpoint, no_results_html, link_col = 1, on_complete=null) {
        this.search_url = search_url;
        this.obj_endpoint = obj_endpoint;
        this.no_results_html = no_results_html;
        this.hidden_cols = ['slug', 'image_path'];
        this.link_col = link_col;
        this.on_complete = on_complete;
        console.log(this.on_complete);
    }


    do_search(query) {

        let params = {
            query: query
        };

        do_get(search_url, params)
            .then(content => this.write_search_results(content))
            .catch(reason => console.log(reason.message));

        if (this.on_complete !== null){
            console.log('test');
                this.on_complete();
            }

    }

    write_search_results(content) {
        this.update_table(
            content['results']['items'], 
            content['results']['columns']
        )

        if (this.on_complete !== null){
            console.log('test');
            this.on_complete();
        }
    }

    update_header(columns) {
        let thead = document.getElementById('table-header-row');
        this.delete_children(thead);
        let hidden_cols = this.hidden_cols;
        columns.forEach(function (column, i) {
            if (!(hidden_cols.includes(column))) {
                let head_col = document.createElement("th");
                head_col.setAttribute('scope', 'col');
                head_col.innerHTML = column.split('_').join(' ');
                head_col.setAttribute('class', 'text-capitalize');
                if (i >1){
                    head_col.setAttribute('class', 'text-capitalize hidden-table-column ');
                }
                thead.append(head_col);
            }

        });
    }

    update_table(rows, columns) {
        this.update_header(columns);
        let link_col = this.link_col;
        let tbody = document.getElementById('tbody');
        
        let hidden_cols = this.hidden_cols;

        this.delete_children(tbody);
        

        if (rows.length == 0) {
            let tr = document.createElement('tr');
            tr.innerHTML = no_results_html;
            tbody.append(tr);
        }
        rows.forEach(function (row) {
            let tr = document.createElement('tr');
            columns.forEach(function (column, i) {
                if (!(hidden_cols.includes(column))) {
                    let td = document.createElement('td');
                    td.setAttribute('class', 'search-result-cell');
                    let cell = document.createElement('div');
                    cell.setAttribute('class', 'search-result-cell');
                    if (i == link_col) {
                        let a = document.createElement('a');
                        a.setAttribute('data-el', row[column]);
                        a.setAttribute('class', 'ticker-chart-link');
                        a.innerHTML = row[column];
                        cell.append(a);
                    } else {
                        cell.innerHTML = row[column];
                    }
                    
                    
                    td.append(cell);
                    tr.append(td);
                }
            });
            tbody.append(tr);
        });
    }

    delete_item(url, slug) {
        let params = {
            slug: slug
        };
        do_post(url, params)
            .then(content => console.log(content))
            .catch(reason => console.log(reason.message));

    }

    delete_children(ele) {
        while (ele.childNodes.length) {
            ele.removeChild(ele.childNodes[0]);
        }
    }


}