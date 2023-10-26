<template>
  <el-table
    :data="upgradeData" 
    :header-cell-style="{fontSize:'14px',background: 'rgb(64 158 255 / 65%)',color:'#696969',}"
    :row-style="{ height: '35px' }" 
    :cell-style="upgradeTableCellStyle" 
    border style="width: 100%">
    <el-table-column prop="resourcepool" label="资源池"  width="120" align="center"> </el-table-column>
    <el-table-column prop="upgradetype" label="类型"  width="50" align="center"> </el-table-column>
    <el-table-column prop="升级次数" label="升级次数"  width="80" align="center"> </el-table-column>
    <el-table-column prop="缺陷" label="缺陷"  width="50" align="center"> </el-table-column>
    <el-table-column prop="需求" label="需求"  width="50" align="center"> </el-table-column>
    <el-table-column prop="优化" label="优化"  width="50" align="center"> </el-table-column>
  </el-table>
</template>


<script>
  export default {
    name : 'upgradeData',
    props: {
      upgradeData: {
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
        console.log('资源池',this.upgradeData[0]['resourcepool'])
    },

    methods: {
      upgradeTableCellStyle(row){
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

<style>
</style>