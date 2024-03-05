<template>
    <div>
        <div>
            受理问题总共 <span style="color: red;">{{ saasProblemTableData[getLastRow()].受理合计 }}次</span>，
            其中bug数量为：<span style="color: red;">{{ saasProblemTableData[summaryRow].产品bug }}个</span>，
            实施配置：<span style="color: red;">{{ saasProblemTableData[summaryRow].实施配置 }}个</span>，
            异常数据处理：<span style="color: red;">{{ saasProblemTableData[summaryRow].异常数据处理 }}次</span>
        </div>
        <div>
            <el-table :data="saasProblemTableData" :row-style="{ height: '30px' }"
                :header-cell-style="{ fontSize: '14px', background: 'rgb(64 158 255 / 65%)', color: '#696969', }"
                style="font-size: 14px; width: 100%; " Boolean border :cell-style="saasTableCellStyle">
                <el-table-column v-for="key in this.saasProblemTableTitle" :key="key" :prop="key" :label="key== '产品bug'? '缺陷合计':key"
                    :width="columnWidth(key)" align="center">
                </el-table-column>
            </el-table>
        </div>
    </div>
</template>
  
  
<script>
export default {
    name: 'saasProblemTableData',
    props: {
        saasProblemTableData: {
            type: Array,
            default() {
                return [];
            },
        },
    },
    data() {
        return {
            summaryRow: this.saasProblemTableData.length - 1,
            saasProblemTableTitle: []
        }
    },
    mounted() {
    },

    watch: {
        saasProblemTableData: {
            handler(newVal, oldVal) {
                this.updateSaasProblemTableTitle(newVal)
            }
        }
    },

    methods: {
        updateSaasProblemTableTitle(newVal){
            var columns = Object.keys(newVal[0])
            columns.splice(-4,4)
            this.saasProblemTableTitle = columns
        },

        getLastRow() {
            // 因为数据进来时候不会自动变化summary row，summary row还是会返回旧的table的最后一行index，所以在这里对summary row进行一个刷新
            this.summaryRow = this.saasProblemTableData.length - 1
            return this.summaryRow
        },

        columnWidth(label) {
            let widthDict = {
                2: 57,
                3: 70,
                4: 78,
                5: 85,
                6: 110,
                10: 130,
            }
            let width
            if (label === "license重置") {
                width = 100
            } else {
                width = widthDict[label.length]
            }
            return width
        },

        saasTableCellStyle(row) {//根据情况显示背景色

            let style = ''
            if (row.rowIndex === this.saasProblemTableData.length - 1) {
                style = 'background: rgb(253 238 32 / 20%);'
            }
            if (row.column.label === "程序版本") {
                style = 'background: rgb(64 158 255 / 50%);'
            } else if (row.column.label === "受理合计") {
                style = 'background: rgb(253 238 32 / 20%); color: red; '
            } else if (row.column.label === "缺陷合计") {
                style = 'background: rgba(245, 108, 108, 0.41); color: blue; '
            }
            style += 'font-size: 14px; '
            return style
        },

    },
}
</script>
  
