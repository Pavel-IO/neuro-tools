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

    this.excludedSubjs = []
    this.excludedRois = []

    this.getFilteredData = () => {
        let filtered = []
        for (let subj of this.rawData) {
            let subjName = subj.name;
            if (!this.excludedSubjs.includes(subjName)) {
                filtered.push(subj)
            }
        }
        return filtered
    }

    this.getFilteredColumns = () => {
        let filtered = [];
        for (let column of this.rawColumns) {
            column.formatter = cellFormater
            if (!this.excludedRois.includes(column.title)) {
                filtered.push(column)
            }
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

function StatsGenerator(dataModel) {
    this.calculateRoisStatsTable = () => {
        let roisStat = []
        let filteredDataset = dataModel.getFilteredData()
        for (column of dataModel.getFilteredColumns()) {
            if (column.field == 'name') {
                continue
            }

            let subjsRoiValues = []
            for (let subject of filteredDataset) {
                subjsRoiValues.push(subject[column.field])
            }

            let stats = new Stats
            lineRecord = {}
            lineRecord.roi = column.title
            lineRecord.mean = Math.round(stats.mean(subjsRoiValues))
            lineRecord.min = Math.round(stats.min(subjsRoiValues))
            lineRecord.q10 = Math.round(stats.quantile(subjsRoiValues, 0.10))
            lineRecord.q25 = Math.round(stats.quantile(subjsRoiValues, 0.25))
            roisStat.push(lineRecord)
        }

        var roisStatColumns = [
            {title: 'Roi', field: 'roi', width: 200, frozen:true},
            {title: 'Minimum', field: 'min', formatter: cellFormater},
            {title: 'Decile', field: 'q10', formatter: cellFormater},
            {title: 'Quartile', field: 'q25', formatter: cellFormater},
            {title: 'Mean', field: 'mean', formatter: cellFormater},
        ]
        return {data: roisStat, columns: roisStatColumns}
    }

    this.calculateSubjsStatsTable = () => {
        let subjsStat = []
        let filteredDataset = dataModel.getFilteredData()
        let filteredColumns = dataModel.getFilteredColumns()
        for (subjRecord of filteredDataset) {

            let roisSubjValues = []
            for (let column of filteredColumns) {
                if (column.field == 'name') {
                    continue
                }
                roisSubjValues.push(subjRecord[column.field])
            }

            let stats = new Stats
            lineRecord = {}
            lineRecord.roi = subjRecord.name
            lineRecord.mean = Math.round(stats.mean(roisSubjValues))
            lineRecord.min = Math.round(stats.min(roisSubjValues))
            lineRecord.q10 = Math.round(stats.quantile(roisSubjValues, 0.10))
            lineRecord.q25 = Math.round(stats.quantile(roisSubjValues, 0.25))
            subjsStat.push(lineRecord)
        }

        var subjsStatColumns = [
            {title: 'Subj', field: 'roi', width:200, frozen:true},
            {title: 'Minimum', field: 'min', formatter: cellFormater},
            {title: 'Decile', field: 'q10', formatter: cellFormater},
            {title: 'Quartile', field: 'q25', formatter: cellFormater},
            {title: 'Mean', field: 'mean', formatter: cellFormater},
        ]
        return {data: subjsStat, columns: subjsStatColumns}
    }
}
