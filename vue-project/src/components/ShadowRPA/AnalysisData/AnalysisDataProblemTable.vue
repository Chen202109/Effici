<template>
    <div>
        <div>
            受理问题总共 <span style="color: red;">{{ problemTableData[getLastRow()].受理合计 }}次</span>，
            其中bug数量为：<span style="color: red;">{{ problemTableData[summaryRow].产品bug }}个</span>，
            实施配置：<span style="color: red;">{{ problemTableData[summaryRow].实施配置 }}个</span>，
            异常数据处理：<span style="color: red;">{{ problemTableData[summaryRow].异常数据处理 }}次</span>
        </div>
        <div>
            <el-table :data="problemTableData" :row-style="{ height: '30px' }"
                :header-cell-style="{ fontSize: '14px', background: 'rgb(64 158 255 / 65%)', color: '#696969', }"
                style="font-size: 14px; width: 100%; " Boolean border :cell-style="saasTableCellStyle">
                <el-table-column v-for="key in this.saasProblemTableTitle" :key="key" :prop="key" :label="key== '产品bug'? '缺陷合计':key"
                    :width="myColumnWidth(key)" align="center">
                </el-table-column>
            </el-table>
        </div>
    </div>
</template>
  
  
<script>
import { columnWidth } from '@/utils/layoutUtil'
export default {
    name: 'problemTableData',
    props: {
        problemTableData: {
            type: Array,
            default() {
                return [];
            },
        },
    },
    data() {
        return {
            summaryRow: this.problemTableData.length - 1,
            saasProblemTableTitle: []
        }
    },
    mounted() {
    },

    watch: {
        problemTableData: {
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
            this.summaryRow = this.problemTableData.length - 1
            return this.summaryRow
        },

        myColumnWidth(label) {
            return columnWidth(label)
        },

        saasTableCellStyle(row) {//根据情况显示背景色

            let style = ''
            if (row.rowIndex === this.problemTableData.length - 1) {
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
  
