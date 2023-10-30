<template>
  <el-table
    :data="licenseData" 
    :header-cell-style="{fontSize:'14px',background: 'rgb(64 158 255 / 65%)',color:'#696969',}"
    border 
    style="width: 100%"
    :cell-style="licenseTableCellStyle">
    <el-table-column prop="省份" label="省份"  width="100" align="center"> 
      <el-table-row>单位申请数</el-table-row>
    </el-table-column>
    <el-table-column v-for="(value, key) in licenseData[0]" :key="key" :prop="key" :label="key" :width="columnWidth(key)" align="center"> </el-table-column>
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

    methods: {
      columnWidth(key) {
        let width
        if (key.length === 2){
          width = 50
        }else if(key.length === 3){
          width = 65
        }
        return width
      },

      licenseTableCellStyle(row){
        console.log(3333333)
        let style = ''
        if(row.column.label==="合计"){
          style =  'background: rgb(253 238 32 / 20%); color: red; '
        }
        return style
      }
    },
  }
</script>

<style>
</style>