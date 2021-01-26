function indexOfSmallest(a) {
    var lowest = 0;
    for (var i = 1; i < a.length; i++) {
        if (a[i] < a[lowest]) lowest = i;
    }
    return lowest;
}

function removeItem(arr, index) {
    arr.splice(index, 1);
    return arr;
}

function Stats() {
    const asc = arr => arr.sort((a, b) => a - b)

    const sum = arr => arr.reduce((a, b) => a + b, 0)

    this.mean = arr => sum(arr) / arr.length

    const std = (arr) => {
        const mu = this.mean(arr);
        const diffArr = arr.map(a => (a - mu) ** 2);
        return Math.sqrt(sum(diffArr) / (arr.length - 1));
    }

    this.quantile = (arr, q) => {
        const sorted = asc(arr);
        const pos = (sorted.length - 1) * q;
        const base = Math.floor(pos);
        const rest = pos - base;
        if (sorted[base + 1] !== undefined) {
            return sorted[base] + rest * (sorted[base + 1] - sorted[base]);
        } else {
            return sorted[base];
        }
    }

    this.min = arr => Math.min(...arr)
}

/*
    table_data.js (generovany):

    var columns = [
        {title:"Subject", field:"name", frozen:true},
        {title:"Precentral_L (1)", field:"roi_1", sorter:"number", headerVertical:true},
    ]

    var tabledata = [
        {name:"581B", id: 0, roi_1: 99, roi_2: 98, roi_3: 97, roi_4: 98, roi_5: 37},
        {name:"600B", id: 1, roi_1: 100, roi_2: 99, roi_3: 100, roi_4: 100, roi_5: 65},
    ]

*/

function DataModel() {
    this.rawData = tabledata    // ted to existuje jako globalni promenna vygenerovana do souboru table_data.js
    this.rawColumns = columns   // ted to existuje jako globalni promenna vygenerovana do souboru table_data.js

    this.getFilteredData = () => {
        let filtered = []
        for (let subj of this.rawData) {
            let subjName = subj.name;
            if (!excluded.includes(subjName)) {
                filtered.push(subj)
            }
        }
        return filtered
    }

    this.getFilteredColumns = () => {
        let filtered = [];
        for (let column of this.rawColumns) {
            column.formatter = cellFormater
            filtered.push(column)
        }
        return filtered
    }

    this.getAllSubjNames = () => {
        let subjNames = []
        for (let subj of this.rawData) {
            subjNames.push(subj.name)
        }
        return subjNames
    }

    this.getAllRoiNames = () => {
        let columnNames = []
        for (let column of this.rawColumns) {
            if (column.title == 'Subject') {  // TODO: skip first, not compare value
                continue
            }
            columnNames.push(column.title)
        }
        return columnNames
    }
}
