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

    this.subjectsChecksListener = (event) => {
        let value = event.target.value
        let checked = event.target.checked
        let index = dataModel.excludedSubjs.indexOf(value)
        // tahle slozitost resi situaci, ktera by vlastne nemela nikdy nastat...
        // ale nektere prohlizece si pamatuji nastaveni formularu pred F5
        if (checked) {
            if (index >= 0) {
                dataModel.excludedSubjs = removeItem(dataModel.excludedSubjs, index)
            }
        } else {
            if (index < 0) {
                dataModel.excludedSubjs.push(value)
            }
        }
        dataModel.excludedSubjs.sort()
        this.updateExcluded()
        this.mainTable.updateRows()
        statsUI.updateStatsListener()
    }

    this.roisChecksListener = (event) => {
        let value = event.target.value
        let checked = event.target.checked
        let index = dataModel.excludedRois.indexOf(value)
        // tahle slozitost resi situaci, ktera by vlastne nemela nikdy nastat...
        // ale nektere prohlizece si pamatuji nastaveni formularu pred F5
        if (checked) {
            if (index >= 0) {
                dataModel.excludedRois = removeItem(dataModel.excludedRois, index)
            }
        } else {
            if (index < 0) {
                dataModel.excludedRois.push(value)
            }
        }
        dataModel.excludedRois.sort()
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
        }
    }

    this.updateExcluded = () => {
        document.getElementById('subjsDisplayExcluded').innerHTML = '<b>Excluded subjects:</b> ' + this.dataModel.excludedSubjs.join(', ')
        document.getElementById('roisDisplayExcluded').innerHTML = '<b>Excluded rois:</b> ' + this.dataModel.excludedRois.join(', ')
    }

    this.init = () => {
        this.createSubjs()
        this.createRois()
        this.updateExcluded()

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
