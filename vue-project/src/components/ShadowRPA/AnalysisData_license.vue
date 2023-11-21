<template>
  <el-table
    :data="tableData" 
    :header-cell-style="{fontSize:'14px',background: 'rgb(64 158 255 / 65%)',color:'#696969',}"
    border 
    style="width: 100%"
    :cell-style="licenseTableCellStyle">
    <el-table-column
      v-for="(item, index) in licenseData"
      :key="index"
      :prop="Object.keys(item)[0]"
      :label="Object.keys(item)[0]"
      :width="columnWidth(Object.keys(item)[0])" align="center">
    </el-table-column>  </el-table>
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
        tableData: []
      }
    },

    watch: {
      licenseData:{
        handler(newVal, oldVal) {
          // 当licenseData发生变化的时候更新tableData
          this.tableData = this.formatTableData(newVal);
        },
        immediate : true //立即执行一次，保证初始化的时候tableData已经被更新
      }
    },

    methods: {
      formatTableData(data) {
        // 转换数据格式以适配el-table
        let formattedData = [];
        data.forEach((item) => {
          const province = Object.keys(item)[0];
          const value = item[province];
          if (!formattedData[0]) {
            formattedData[0] = {};
          }
          formattedData[0][province] = value;
        });
        return formattedData;
      },

      columnWidth(key) {
        let width
        if (key === "省份"){
          width = 100
        }else if (key.length === 2){
          width = 50
        }else if(key.length === 3){
          width = 65
        }
        return width
      },

      licenseTableCellStyle(row){
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