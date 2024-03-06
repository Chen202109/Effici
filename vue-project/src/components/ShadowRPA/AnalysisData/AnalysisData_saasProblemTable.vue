<template>
    <div>
        <!-- 周末要发的受理信息数据-->
        <div>
            受理问题总共 <span style="color: red;">{{ saasProblemTableData[getLastRow()].total }}次</span>，其中bug数量为：<span
                style="color: red;">{{ saasProblemTableData[summaryRow].softbug
                }}个</span>，
            实施配置：<span style="color: red;">{{ saasProblemTableData[summaryRow].sspz }}个</span>，异常数据处理：<span style="color: red;">{{
                saasProblemTableData[summaryRow].ycsjcl }}次</span>
        </div>
        <div>
            <el-table :data="saasProblemTableData" :row-style="{ height: '30px' }"
                :header-cell-style="{ fontSize: '14px', background: 'rgb(64 158 255 / 65%)', color: '#696969', }"
                style="font-size: 14px; width: 100%; " Boolean border :cell-style="saasTableCellStyle">
                <el-table-column prop="softversion" label="程序版本" width="80" align="center"> </el-table-column>
                <el-table-column v-for="(item, index) in tableTitle" :key="index" :prop="item.prop" :label="item.label"
                :width="myColumnWidth(item.label)" align="center"> </el-table-column>
            </el-table>
        </div>
    </div>
</template>
  
  
<script>
import { columnWidth } from '@/utils/layoutUtil'
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
            summaryRow : this.saasProblemTableData.length - 1,
            tableTitle: [
                { prop: 'total', label: '受理合计' },
                { prop: 'report', label: '报表功能' },
                { prop: 'openbill', label: '开票功能' },
                { prop: 'licenseReset', label: 'license重置' },
                { prop: 'added', label: '增值服务' },
                { prop: 'collection', label: '收缴业务' },
                { prop: 'exchange', label: '通知交互' },
                { prop: 'writeoff', label: '核销功能' },
                { prop: 'billManagement', label: '票据管理' },
                { prop: 'security', label: '安全漏洞' },
                { prop: 'print', label: '打印功能' },
                { prop: 'datasync', label: '数据同步' },
                { prop: 'inverse', label: '反算功能' },
                { prop: 'opening', label: '单位开通' },
                { prop: 'softbug', label: '缺陷合计' },
            ],
        }
    },
    mounted() {

    },

    methods: {
        getLastRow(){
            // 因为数据进来时候不会自动变化summary row，summary row还是会返回旧的table的最后一行index，所以在这里对summary row进行一个刷新
            this.summaryRow = this.saasProblemTableData.length - 1
            return this.summaryRow
        },

        myColumnWidth(key) {
            // let width
            // if (key === "license重置"){
            //     width = 100
            // }else {
            //     width = 78
            // }
            // return width
            return columnWidth(key)
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
  
<style></style>