var cellFormater = (cell, formatterParams) => {
    var value = cell.getValue()
    if (Number.isInteger(value)){
        let color = ''
        if (value < 25) {
            color = 'red'
        } else if (value < 50) {
            color = '#ff9e44'
        }
        if (color) {
            return '<span style="color:' + color + '; font-weight:bold;">' + value + "</span>"
        } else {
            return value
        }
    } else {
        return value
    }
}

function MainUI(dataModel) {
    this.dataModel = dataModel
    this.subjCheckObjs = []
    this.roiCheckObjs = []

    this.docText = (id, text) => {
        document.getElementById(id).innerText = text
    }
    this.docVal = (id, text) => {
        document.getElementById(id).value = text
    }

    this.subjectsChecksListener = (event) => {
        dataModel.setSubjActive(event.target.value, event.target.checked)
        this.updateExcluded()
        this.mainTable.updateRows()
        statsUI.updateStatsListener()
    }

    this.roisChecksListener = (event) => {
        dataModel.setRoiActive(event.target.value, event.target.checked)
        this.updateExcluded()
        this.mainTable.updateColumns()
        statsUI.updateStatsListener()
    }

    this.createSubjs = () => {
        let subjs = this.dataModel.getAllSubjNames()
        for (let k = 0; k < subjs.length; k++) {
            let html = '<input type="checkbox" id="subj' + k + '" value="' + subjs[k] + '"> <label for="subj' + k + '">' + subjs[k] + '</label><br>'
            document.getElementById('subjsCheckboxes').innerHTML += html
        }
        // toto nemuze byt v jednom cyklu, dokud se appenduji html a furt ho prepisuji, mazu si event listenery
        for (let k = 0; k < subjs.length; k++) {
            let obj = document.getElementById('subj' + k)
            obj.checked = true
            obj.onchange = this.subjectsChecksListener
            this.subjCheckObjs.push(obj)
        }
    }

    this.createRois = () => {
        let rois = this.dataModel.getAllRoiNames()
        for (let k = 0; k < rois.length; k++) {
            let html = '<input type="checkbox" id="roi' + k + '" value="' + rois[k] + '"> <label for="roi' + k + '">' + rois[k] + '</label><br>'
            document.getElementById('roisCheckboxes').innerHTML += html
        }
        // toto nemuze byt v jednom cyklu, dokud se appenduji html a furt ho prepisuji, mazu si event listenery
        for (let k = 0; k < rois.length; k++) {
            let obj = document.getElementById('roi' + k)
            obj.checked = true
            obj.onchange = this.roisChecksListener
            this.roiCheckObjs.push(obj)
        }
    }

    this.updateExcluded = () => {
        this.docText('excludedSubjsCount', this.dataModel.excludedSubjs.length)
        this.docText('allSubjsCount', this.dataModel.getAllRowsCount())
        this.docVal('subjsDisplayExcluded', this.dataModel.excludedSubjs.join(', '))

        this.docText('excludedRoisCount', this.dataModel.excludedRois.length)
        this.docText('allRoisCount', this.dataModel.getAllColumnsCount())
        this.docVal('roisDisplayExcluded', this.dataModel.excludedRois.join(', '))
    }

    this.updateSubjsSearch = () => {
        let subjsInputObj = document.getElementById('subjsSearchThr')
        let lowerSubjs = this.dataModel.getSubjsByCoverage(parseInt(subjsInputObj.value))
        this.docText('subjsSearchCount', lowerSubjs.length)
    }

    this.updateRoisSearch = () => {
        let roisInputObj = document.getElementById('roisSearchThr')
        let lowerRois = this.dataModel.getRoisByCoverage(parseInt(roisInputObj.value))
        this.docText('roisSearchCount', lowerRois.length)
    }

    this.createSubjsSearch = () => {
        let subjsInputObj = document.getElementById('subjsSearchThr')
        subjsInputObj.value = 50
        subjsInputObj.onchange = this.updateSubjsSearch

        let subjsExcludeObj = document.getElementById('subjsSearchExclude')
        subjsExcludeObj.onclick = () => {
            let subjInputObj = document.getElementById('subjsSearchThr')
            for (let subj of this.dataModel.getSubjsByCoverage(parseInt(subjInputObj.value))) {
                this.dataModel.setSubjActive(subj, false)
            }
            this.globalUpdateSubjs()
            for (let obj of this.subjCheckObjs) {
                obj.checked = dataModel.isSubjActive(obj.value)
            }
        }
    }

    this.createRoisSearch = () => {
        let subjsInputObj = document.getElementById('roisSearchThr')
        subjsInputObj.value = 50
        subjsInputObj.onchange = this.updateRoisSearch

        let roisExcludeObj = document.getElementById('roisSearchExclude')
        roisExcludeObj.onclick = () => {
            let roisInputObj = document.getElementById('roisSearchThr')
            for (let roi of this.dataModel.getRoisByCoverage(parseInt(roisInputObj.value))) {
                this.dataModel.setRoiActive(roi, false)
            }
            this.globalUpdateRois()
            for (let obj of this.roiCheckObjs) {
                obj.checked = dataModel.isRoiActive(obj.value)
            }
        }
    }

    this.globalUpdateSubjs = () => {
        this.updateExcluded()
        this.updateSubjsSearch()
        this.mainTable.updateRows()
        statsUI.updateStatsListener()
    }

    this.globalUpdateRois = () => {
        this.updateExcluded()
        this.updateRoisSearch()
        this.mainTable.updateColumns()
        statsUI.updateStatsListener()
    }

    this.init = () => {
        this.createSubjs()
        this.createRois()
        this.createSubjsSearch()
        this.createRoisSearch()
        this.updateExcluded()
        this.updateSubjsSearch()
        this.updateRoisSearch()
        this.mainTable = new MainTable(this.dataModel)
    }
}

function StatsUI(statsGenerator) {
    this.showOnlyMainTable = () => {
        document.getElementById('statsTablePanel').style.display = 'none'
        document.getElementById('mainTablePanel').style.width = '98%'
    }

    this.showStatsAndMainTable = () => {
        document.getElementById('statsTablePanel').style.display = 'inline-block'
        document.getElementById('mainTablePanel').style.width = '60%'
    }

    this.updateStatsListener = () => {
        let showRois = document.getElementById('show_rois').checked
        let showSubjs = document.getElementById('show_subjs').checked
        if (showRois) {
            this.showStatsAndMainTable()
            this.statsTable.update(statsGenerator.calculateRoisStatsTable())
        } else if (showSubjs) {
            this.showStatsAndMainTable()
            this.statsTable.update(statsGenerator.calculateSubjsStatsTable())
        } else {
            this.showOnlyMainTable()
        }
    }

    this.init = () => {
        let statsControls = ['show_rois', 'show_subjs', 'show_none']
        document.getElementById('show_rois').checked = true
        for (let control of statsControls) {
            document.getElementById(control).onchange = this.updateStatsListener
        }
        this.statsTable = new StatsTable(statsGenerator)
    }
}

function MainTable(dataModel) {
    this.table = new Tabulator('#mainTablePanel', {
        data: dataModel.getFilteredData(),
        height: '600px',
        columns: dataModel.getFilteredColumns(),
    })

    this.updateRows = () => {
        this.table.setFilter('name', 'in', dataModel.getFilteredSubjs())
    }

    this.updateColumns = () => {
        for (let c of dataModel.getSHColumns()) {
            if (c.show) {
                this.table.showColumn(c.column)
            } else {
                this.table.hideColumn(c.column)
            }
        }
    }
}

function StatsTable(statsGenerator) {
    var roiStatsTable = statsGenerator.calculateRoisStatsTable()
    this.statsTable = new Tabulator("#statsTablePanel", {
        data: roiStatsTable.data,
        height: '600px',
        columns: roiStatsTable.columns,
    })

    this.update = (newDataset) => {
        this.statsTable.setColumns(newDataset.columns)
        this.statsTable.replaceData(newDataset.data)
    }
}
