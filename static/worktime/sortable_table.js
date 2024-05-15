function sort_table(table, index, order) {
    if (table.rows.length < 3) return;
    const rows = [];
    const parent_r = table.rows[1].parentElement;
    let numeric = true;
    for (let i = 1; i < table.rows.length; i++) {
        const record = {};
        record.row = table.rows[i];
        const cell = table.rows[i].cells[index];
        record.key = cell.hasAttribute('data-sort') ? cell.getAttribute('data-sort') : cell.textContent;
        rows.push(record);
        if (isNaN(record.key)) {
            numeric = false;
        }
    }
    rows.sort((a, b) => {
        const text1 = a.key;
        const text2 = b.key;
        let cond;
        if (numeric) {
            cond = Number(text1) - Number(text2);
        } else {
            cond = text1.localeCompare(text2);
        }
        return cond * (order ? 1 : -1);
    });
    for (let i = 0; i < rows.length; i++) {
        parent_r.appendChild(rows[i].row);
    }
}

function init_sortable_table() {
    const tables = document.querySelectorAll('table.sortable');
    for (let i = 0; i < tables.length; i++) {
        const table = tables[i];
        const headers = table.rows[0];
        for (let j = 0; j < headers.cells.length; j++) {
            const cell = headers.cells[j];
            cell.classList.add('sort-none');
            cell.addEventListener('click', function () {
                let index = -1;
                let order = !this.classList.contains('sort-asc');
                for (let k = 0; k < headers.cells.length; k++) {
                    const header = headers.cells[k];
                    if (this == header) {
                        index = k;
                        if (order) {
                            header.classList.remove('sort-none', 'sort-desc');
                            header.classList.add('sort-asc');
                        } else {
                            header.classList.remove('sort-none', 'sort-asc');
                            header.classList.add('sort-desc');
                        }
                    } else {
                        header.classList.remove('sort-asc', 'sort-desc');
                        header.classList.add('sort-none');
                    }
                }
                sort_table(table, index, order);
            });
        }
    }
}

window.addEventListener('load', init_sortable_table);