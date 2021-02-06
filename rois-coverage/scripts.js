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

    this.excludeSubj = (subj) => {
        this.excludedSubjs.push(subj)  // TODO: radeji hlidat duplicity (i kvuli pozdejsimu mazani)
        this.excludedSubjs.sort()
    }

    this.getFilteredData = () => {
        return this.rawData.filter(subj => !this.excludedSubjs.includes(subj.name))
    }

    this.getFilteredSubjs = () => {
        return this.getFilteredData().map(subj => subj.name)
    }

    this.getFilteredColumns = () => {
        return this.rawColumns.filter(column => !this.excludedRois.includes(column.title))
                                .map(column => { column.formatter = cellFormater; return column })
    }

    this.getRoisByCoverage = (coverageThr) => {
        let stats = new Stats
        let result = []
        let rowsCache = this.getFilteredData()
        for (let roi of this.getFilteredColumns()) {
            let buffer = []
            for (let subj of rowsCache) {
                buffer.push(subj[roi.field])
            }
            let q10 = Math.round(stats.quantile(buffer, 0.10))
            if (q10 <= coverageThr) {
                result.push(roi.title)
            }
        }
        return result
    }

    this.getSubjsByCoverage = (coverageThr) => {
        let columnsCache = this.getFilteredColumns()
        let isSubjSmallerThanCoverage = (subj, coverageThr) =>
            columnsCache.find(roi => subj[roi.field] <= coverageThr) !== undefined

        return this.getFilteredData().filter(subj => isSubjSmallerThanCoverage(subj, coverageThr))
                                        .map(subj => subj.name)
    }

    this.getSHColumns = () => {
        let filtered = [];
        for (let column of this.rawColumns) {
            filtered.push({column: column.field, show: !this.excludedRois.includes(column.title)})
        }
        return filtered
    }

    this.getAllSubjNames = () => {
        return this.rawData.map(subj => subj.name)
    }

    this.getAllRoiNames = () => {
        return this.rawColumns.slice(1).map(column => column.title)
    }

    this.getAllRowsCount = () => {
        return this.rawData.length
    }

    this.getAllColumnsCount = () => {
        return this.rawColumns.length
    }
}

function StatsGenerator(dataModel) {
    this.calculateRoisStatsTable = () => {
        let stats = new Stats
        let roisStat = []
        let filteredDataset = dataModel.getFilteredData()
        for (column of dataModel.getFilteredColumns().slice(1)) {
            let subjsRoiValues = filteredDataset.map(subject => subject[column.field])
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
        let stats = new Stats
        let subjsStat = []
        let filteredColumns = dataModel.getFilteredColumns()
        for (subjRecord of dataModel.getFilteredData()) {
            let roisSubjValues = filteredColumns.slice(1).map(column => subjRecord[column.field])
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
