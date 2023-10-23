<template>
  <el-table
    :data="licenseData" :header-cell-style="{ background:'#DDDDDD',color:'#000'}" border style="width: 100%">
    <el-table-column v-if="licenseData[0]['省份']" prop="省份" label="省份"  width="100" align="center"> </el-table-column>
    <el-table-column v-if="licenseData[0]['北京']" prop="北京" label="北京"  width="50" align="center"> </el-table-column>
    <el-table-column v-if="licenseData[0]['山西']" prop="山西" label="山西"  width="50" align="center"> </el-table-column>
    <el-table-column v-if="licenseData[0]['内蒙古']" prop="内蒙古" label="内蒙古" width="65" align="center"> </el-table-column>
    <el-table-column v-if="licenseData[0]['辽宁']" prop="辽宁" label="辽宁"  width="50" align="center"> </el-table-column>
    <el-table-column v-if="licenseData[0]['吉林']" prop="吉林" label="吉林"  width="50" align="center"> </el-table-column>
    <el-table-column v-if="licenseData[0]['黑龙江']" prop="黑龙江" label="黑龙江"  width="65" align="center"> </el-table-column>
    <el-table-column v-if="licenseData[0]['上海']" prop="上海" label="上海"  width="50" align="center"> </el-table-column>
    <el-table-column v-if="licenseData[0]['安徽']" prop="安徽" label="安徽"  width="50" align="center"> </el-table-column>
    <el-table-column v-if="licenseData[0]['福建']" prop="福建" label="福建"  width="50" align="center"> </el-table-column>
    <el-table-column v-if="licenseData[0]['江西']" prop="江西" label="江西"  width="50" align="center"> </el-table-column>
    <el-table-column v-if="licenseData[0]['山东']" prop="山东" label="山东"  width="50" align="center"> </el-table-column>
    <el-table-column v-if="licenseData[0]['河南']" prop="河南" label="河南"  width="50" align="center"> </el-table-column>
    <el-table-column v-if="licenseData[0]['湖北']" prop="湖北" label="湖北"  width="50" align="center"> </el-table-column>
    <el-table-column v-if="licenseData[0]['广东']" prop="广东" label="广东"  width="50" align="center"> </el-table-column>
    <el-table-column v-if="licenseData[0]['广西']" prop="广西" label="广西"  width="50" align="center"> </el-table-column>
    <el-table-column v-if="licenseData[0]['海南']" prop="海南" label="海南"  width="50" align="center"> </el-table-column>
    <el-table-column v-if="licenseData[0]['重庆']" prop="重庆" label="重庆"  width="50" align="center"> </el-table-column>
    <el-table-column v-if="licenseData[0]['四川']" prop="四川" label="四川"  width="50" align="center"> </el-table-column>
    <el-table-column v-if="licenseData[0]['贵州']" prop="贵州" label="贵州"  width="50" align="center"> </el-table-column>
    <el-table-column v-if="licenseData[0]['云南']" prop="云南" label="云南"  width="50" align="center"> </el-table-column>
    <el-table-column v-if="licenseData[0]['西藏']" prop="西藏" label="西藏"  width="50" align="center"> </el-table-column>
    <el-table-column v-if="licenseData[0]['陕西']" prop="陕西" label="陕西"  width="50" align="center"> </el-table-column>
    <el-table-column v-if="licenseData[0]['甘肃']" prop="甘肃" label="甘肃"  width="50" align="center"> </el-table-column>
    <el-table-column v-if="licenseData[0]['青海']" prop="青海" label="青海"  width="65" align="center"> </el-table-column>
    <el-table-column v-if="licenseData[0]['宁夏']" prop="宁夏" label="宁夏"  width="50" align="center"> </el-table-column>
    <el-table-column v-if="licenseData[0]['新疆']" prop="新疆" label="新疆"  width="50" align="center"> </el-table-column>
    <el-table-column prop="合计" label="合计"  width="50" align="center"> </el-table-column>
  </el-table>
</template>


<script>
  export default {
    name : 'licenseData',
    props: {
      licenseData: {
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
        console.log('北京',this.licenseData[0]['北京'],'上海',this.licenseData[0]['上海'])
    },
  }
</script>

<style>
<style>