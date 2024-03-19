<template>
    <div class="privatizationLicense">
        <div style="margin: 15px 0">
            <span class="demonstration" style="margin-left: 15px;">时间范围： </span>
            <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期"
                end-placeholder="结束日期">
            </el-date-picker>
            <el-button type="primary" @click="search">查询</el-button>
        </div>
        <div>
            <p class="saasAnalysisTitle"> {{ licenseRegisterProvinceData['seriesName'] }}</p>
            <el-table
            :data="licenseRegisterProvinceTableData" 
            :header-cell-style="{fontSize:'14px',background: 'rgb(64 158 255 / 65%)',color:'#696969',}"
            border style="width: 100%" :cell-style="licenseTableCellStyle">
                <el-table-column
                v-for="(item, index) in licenseRegisterProvinceData['seriesData']" :key="index" :prop="Object.keys(item)[0]" :label="Object.keys(item)[0]"
                :width="columnWidth(Object.keys(item)[0])" align="center">
                </el-table-column>  
            </el-table>
        </div>
    </div>
</template>
  
  
<script>
    export default {
      name : 'AnalysisPrivatizationLicense',
      data() {
        return {
            // 日期查询范围
            dateRange: [new Date(new Date().getFullYear() + '-' + (new Date().getMonth() + 1) + '-01'),new Date()],

            licenseRegisterProvinceData: [{'seriesName': "", 'seriesData': ""}],
            licenseRegisterProvinceTableData: [],
        }
      },
  
      methods: {
        
        /**
         * 转换数据格式以适配el-table
         * @param {*} licenseData 
         */
        formatRegisterTableData(licenseRegisterData) {
          let formattedData = [];
          licenseRegisterData.forEach((item) => {
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
        },

        /**
         * 按下查询按钮之后异步查询更新页面图标数据。
         */
         async search() {
            // 触发查询事件，根据日期条件进行查询
            var searchValue = {} // 存放筛选条件信息
            // 获取年、月、日，进行拼接
            for (let i = 0; i < this.dateRange.length; i++) {
                var year = this.dateRange[i].getFullYear()
                var month = ('0' + (this.dateRange[i].getMonth() + 1)).slice(-2)
                var day = ('0' + this.dateRange[i].getDate()).slice(-2)
                searchValue[(i==0)?"beginData":"endData"] = year + "-" + month + "-" + day;
            } //结束for，完成日期的拼接

            this.saasPrivatizationLicenseProvince(searchValue)
        },

        /**
         * @param {searchValue} searchValue 搜索参数的字典
         * @description 对私有化license发放的省份统计的后端数据请求
         */
         async saasPrivatizationLicenseProvince(searchValue) {
          this.$http.get(
            '/api/CMC/workrecords/analysis_saas_privatization_license_register_province?beginData=' +
            searchValue['beginData'] +
            '&endData=' +
            searchValue['endData']
          ).then(response => {
            this.licenseRegisterProvinceData = response.data
            this.licenseRegisterProvinceTableData = this.formatRegisterTableData(this.licenseRegisterProvinceData['seriesData']);
            console.log('update local licenseRegisterProvinceData data: ', this.licenseRegisterProvinceData)
          }).catch((error) => {
            console.log("失败" + error)
            this.$message.error('错了哦，仔细看错误信息弹窗')
            alert('失败' + error)
          })
        },
      },
    }
  </script>
  
  <style scoped>
    .saasAnalysisTitle {
        color: #3398DB;
        font-size: 18;
        margin: 5px 10px 5px 0;
    }
  </style>