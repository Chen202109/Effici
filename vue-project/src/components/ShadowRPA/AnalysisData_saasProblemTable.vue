<template>
    <!-- 周末要发的受理信息数据-->
    <div>
        受理问题总共 <span style="color: red;">{{ all_total }}次</span>，其中bug数量为：<span style="color: red;">{{ all_softbug
        }}个</span>，
        实施配置：<span style="color: red;">{{ all_sspz }}个</span>，异常数据处理：<span style="color: red;">{{ all_ycsjcl }}次</span>
    </div>
    <div>
        <el-table :data="tableData" :row-style="{ height: '30px' }"
            :header-cell-style="{ fontSize: '14px', background: 'rgb(64 158 255 / 65%)', color: '#696969', }"
            style="font-size: 14px; width: 100%; " Boolean border :cell-style="saasTableCellStyle">
            <el-table-column prop="softversion" label="程序版本" width="80" align="center"> </el-table-column>
            <el-table-column v-for="(item, index) in tableTitle" :key="index" :prop="item.prop" :label="item.label"
                width="78" align="center"> </el-table-column>
        </el-table>
    </div>
</template>
  
  
<script>
export default {
    name: 'saasProblemTable',
    props: {
        tableData: {
            type: Array,
            default() {
                return [];
            },
        },
    },
    data() {
        return {

        }
    },
    mounted() {

    },

    methods: {
        upgradeTableCellStyle(row) {
            let style = ''
            if (row.rowIndex === this.upgradeData.length - 1) {
                style = 'background: rgb(253 238 32 / 20%);'
            }
            style += 'font-size: 14px; '
            return style
        }
    },
}
</script>
  
<style></style>