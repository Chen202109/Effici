<template>
  <el-table
    :data="upgradeData" :header-cell-style="{ background:'#DDDDDD',color:'#000'}" 
    :row-style="{ height: '35px' }" :cell-style="{padding:'0px'}" border style="width: 100%" show-summary>
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
    name : 'licenseData',
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
        // tableData: [{
        //   date: '2016-05-03',
        //   name: '王小虎',
        //   address: '上海市普陀区金沙江路 1518 弄'
        // }]
      }
    },
    mounted() {
        console.log('资源池',this.upgradeData[0]['resourcepool'])
    },
  }
</script>

<style>
<style>