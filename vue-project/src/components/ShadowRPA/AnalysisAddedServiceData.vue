<template>
    <div>
        <div style="margin: 15px 0">
            <span class="demonstration" style="margin-left: 15px;">省份： </span>
            <el-select v-model = "provinceSelected" placeholder = "请选择省份" style="width: 120px;" :clearable="true">
                <el-option v-for="(item,index) in this.provinceList" :key="index" :label="item.region" :value="item.region"></el-option>
            </el-select>
            <span class="demonstration" style="margin-left: 15px;">时间范围： </span>
            <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期"
                end-placeholder="结束日期">
            </el-date-picker>
            <el-button type="primary" @click="search">查询</el-button>
        </div>

        <div class="saasAddedServiceTypeProvinceChart" id="saasAddedServiceTypeProvinceChart" :style="{ width: getPageWidth + 'px', height: '400px' }">
        </div>

        <div class="saasAddedServiceProvinceChart" id="saasAddedServiceProvinceChart"
            :style="{ width: getPageWidth + 'px', height: '400px' }">
        </div>

        <div>
            <div class="saasAddedServiceTypeChart" id="saasAddedServiceTypeChart" :style="{ width: getPageWidth * 0.65+ 'px', height: '600px' }">
            </div>
            <div class="saasAddedServiceTopTable" style="width: 35%;">
                <p>{{ saasAddedServiceTypeChartData[2]['seriesName'] }}: <span style="color: red;">{{ saasAddedServiceTypeChartData[2]['seriesData'] }}</span> 次</p>
                <el-table
                :data="saasAddedServiceTypeChartData[1]['seriesData']" 
                :header-cell-style="{fontSize:'14px',background: 'rgb(64 158 255 / 65%)',color:'#696969',}"
                :cell-style="{fontSize: 12 + 'px',}"
                style="width: 100%; margin: auto">
                <el-table-column :label="saasAddedServiceTypeChartData[1].seriesName" align="center">
                    <el-table-column
                    v-for="(item, index) in saasAddedServiceTopTableTitle" :key="index" :prop="item.prop" :label="item.label"
                    :width="columnWidth(item.label, 'saasAddedServiceTopTable')"  align="center">
                    </el-table-column>
                </el-table-column>  
                </el-table>
            </div>
    </div>
    </div>
</template>
  
<script>
import { getMainPageWidth } from '@/utils/layoutUtil'
import { updateBarChartBasic, updatePieChartBasic } from '@/utils/echartBasic'

// 引入基本模板
let echarts = require("echarts/lib/echarts");
// 引入提示框和title组件
require("echarts/lib/component/tooltip");
require("echarts/lib/component/title");

export default {
    name: 'AnalysisAddedServiceData',
    data() {
        return {
            // 日期查询范围
            dateRange: [new Date(new Date().getFullYear() + '-01-01'), new Date()],
            // 省份
            provinceList : [],
            provinceSelected: '',
            // 增值服务表头的数据
            saasAddedServiceTopTableTitle: [
                {'prop': "name", "label": "增值服务分类"},
                {'prop': "value", "label": "次数"},
                {'prop': "percent", "label": "百分比"}
            ],

            saasAddedServiceProvinceChartData: [],
            saasAddedServiceTypeChartData: [ 
                {'seriesName': "增值服务分类", 'seriesData': []}, 
                {'seriesName': "增值服务top10", 'seriesData': []}, 
                {'seriesName': "增值服务合计", 'seriesData': 0}
            ],
        }
    },
    // 计算页面刚加载时候渲染的属性
    computed: {
        getPageWidth: getMainPageWidth
    },
    mounted() {
        this.searchAddedServiceProvinceList()
        this.drawLine();
    },
    methods: {
        /**
         * 计算el-table列的宽度
         */
        columnWidth(key, tableName) {
            key= key.replace(/_/g, '').replace(/[^\w\u4e00-\u9fa50-9]/g, "")
            let widthDict = {
                2: 57,
                3: 70,
                4: 75,
                5: 85,
                6: 110,
                10: 130,
            }
            let width
            if (tableName === 'saasAddedServiceTopTable' && key === '增值服务分类') {
                width = 220
            } else if (key.length in widthDict){
                width = widthDict[key.length]
            }
            return width
        },

        /**
         * 用于使用echarts进行图标的基础绘制init
         */
        drawLine() {
            echarts.init(document.getElementById('saasAddedServiceTypeProvinceChart'))
            echarts.init(document.getElementById('saasAddedServiceProvinceChart'))
            echarts.init(document.getElementById('saasAddedServiceTypeChart'))
        },

        /**
         * 按下查询按钮之后异步查询更新页面图标数据。
         */
        async search() {
            // 触发查询事件，根据日期条件进行查询
            var searchValue = {} // 存放筛选条件信息
            searchValue['provinceSelected'] = this.provinceSelected
            // 获取年、月、日，进行拼接
            for (let i = 0; i < this.dateRange.length; i++) {
                var year = this.dateRange[i].getFullYear()
                var month = ('0' + (this.dateRange[i].getMonth() + 1)).slice(-2)
                var day = ('0' + this.dateRange[i].getDate()).slice(-2)
                searchValue[(i==0)?"beginData":"endData"] = year + "-" + month + "-" + day;
            } //结束for，完成日期的拼接

            this.saasAddedServiceTypeProvince(searchValue)
            this.saasAddedServiceProvince(searchValue)
            this.searchSaaSAddedServiceByType(searchValue)
        },

        /**
         * 对增值服务的省份列表的后端数据请求
         */
         searchAddedServiceProvinceList(){
            var searchValue = {} // 存放筛选条件信息
            searchValue['provinceSelected'] = this.provinceSelected
            // 获取年、月、日，进行拼接 
            for (let i = 0; i < this.dateRange.length; i++) {
                var year = this.dateRange[i].getFullYear()
                var month = ('0' + (this.dateRange[i].getMonth() + 1)).slice(-2)
                var day = ('0' + this.dateRange[i].getDate()).slice(-2)
                searchValue[(i==0)?"beginData":"endData"] = year + "-" + month + "-" + day;
            } 
            this.$http.get(
                '/api/CMC/workrecords/analysis_saas_added_service_province_list'
            ).then(response =>{
                this.provinceList = response.data.data[0]["seriesData"]
                if (this.provinceList.length !== 0){
                    this.provinceSelected = this.provinceList[0].region
                }
            }).catch(error =>{
                console.log(error)
                this.$message.error('错了哦，仔细看错误信息弹窗')
                alert('失败' + error)
            })
        },

        /**
         * @param {searchValue} searchValue 搜索参数的字典
         * @description 对增值服务的服务分类关于省份分类的后端数据请求
         */
         async saasAddedServiceTypeProvince(searchValue) {
            try {
                const response = await this.$http.get(
                '/api/CMC/workrecords/analysis_saas_added_service_by_function_and_province?beginData=' +
                searchValue['beginData'] +
                '&endData=' +
                searchValue['endData']+
                '&provinceSelected=' +
                searchValue['provinceSelected']
                )
                this.saasAddedServiceTypeProvinceChartData = response.data.data
                updateBarChartBasic(document, this.saasAddedServiceTypeProvinceChartData, '省份增值服务类型统计', "category", false, true, 'saasAddedServiceTypeProvinceChart')
                console.log('update local saasAddedServiceTypeProvinceChart data: ', this.saasAddedServiceTypeProvinceChartData)

            } catch (error) {
                console.log(error)
                this.$message.error('错了哦，仔细看错误信息弹窗')
                alert('失败' + error)
            }
        },

        /**
         * @param {searchValue} searchValue 搜索参数的字典
         * @description 对增值服务的关于省份的受理数量的后端数据请求
         */
        async saasAddedServiceProvince(searchValue) {
            try {
                const response = await this.$http.get(
                '/api/CMC/workrecords/analysis_saas_added_service_by_province?beginData=' +
                searchValue['beginData'] +
                '&endData=' +
                searchValue['endData']
                )
                this.saasAddedServiceProvinceChartData = response.data.data
                updateBarChartBasic(document, this.saasAddedServiceProvinceChartData, '省份增值服务数量统计', "category", false, true, 'saasAddedServiceProvinceChart')
                console.log('update local saasAddedServiceProvinceChart data: ', this.saasAddedServiceProvinceChartData)

            } catch (error) {
                console.log(error)
                this.$message.error('错了哦，仔细看错误信息弹窗')
                alert('失败' + error)
            }
        },

        /**
         * @param {searchValue} searchValue 搜索参数的字典
         * @description 对增值服务的服务类别的饼状图的后端数据请求
         */
        async searchSaaSAddedServiceByType(searchValue) {
            try {
                const response = await this.$http.get(
                '/api/CMC/workrecords/analysis_saas_added_service_by_function?beginData=' +
                searchValue['beginData'] +
                '&endData=' +
                searchValue['endData']
                )
                this.saasAddedServiceTypeChartData = response.data.data
                updatePieChartBasic(document, this.saasAddedServiceTypeChartData, "增值服务分类", "saasAddedServiceTypeChart")
                console.log('update local saasAddedServiceTypeChart data: ', this.saasAddedServiceTypeChartData)

            } catch (error) {
                console.log(error)
                this.$message.error('错了哦，仔细看错误信息弹窗')
                alert('失败' + error)
            }
        },
    },
};
</script>

<style>
.saasAddedServiceTypeChart {
  display: inline-block;
}

.saasAddedServiceTopTable {
  display: inline-block;
}
</style>