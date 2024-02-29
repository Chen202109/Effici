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

        <div class="saasMonitorProblemTypeProvinceChart" id="saasMonitorProblemTypeProvinceChart" :style="{ width: getPageWidth + 'px', height: '400px' }">
        </div>

        <div class="saasMonitorProblemProvinceChart" id="saasMonitorProblemProvinceChart" :style="{ width: getPageWidth + 'px', height: '400px' }">
        </div>

        <div>
            <div class="saasMonitorProblemTypeChart" id="saasMonitorProblemTypeChart" :style="{ width: getPageWidth * 0.65+ 'px', height: '600px' }">
            </div>
            <div class="saasMonitorProblemTopTable" style="width: 35%;">
                <p>{{ saasMonitorProblemTypeChartData[2]['seriesName'] }}: <span style="color: red;">{{ this.saasMonitorProblemCount }}</span> 次</p>
                <el-table
                :data="saasMonitorProblemTypeChartData[1]['seriesData']" 
                :header-cell-style="{fontSize:'14px',background: 'rgb(64 158 255 / 65%)',color:'#696969',}"
                :cell-style="{fontSize: 12 + 'px',}"
                style="width: 100%; margin: auto">
                <el-table-column :label="saasMonitorProblemTypeChartData[1].seriesName" align="center">
                    <el-table-column
                    v-for="(item, index) in saasMonitorProblemTopTableTitle" :key="index" :prop="item.prop" :label="item.label"
                    :width="columnWidth(item.label, 'saasMonitorProblemTopTable')"  align="center">
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
    name: 'AnalysisThirdPartyProblem',
    data() {
        return {
            // 日期查询范围
            dateRange: [new Date(new Date().getFullYear() + '-01-01'), new Date()],
            // 省份
            provinceList : [],
            provinceSelected: '',
            // 监控异常的数据的表格的表头
            saasMonitorProblemTopTableTitle: [
                {'prop': "name", "label": "问题分类"},
                {'prop': "value", "label": "次数"},
                {'prop': "percent", "label": "百分比"}
            ],
            // 监控异常的图表的数据
            saasMonitorProblemTypeProvinceChartData: [],
            saasMonitorProblemProvinceChartData: [],
            saasMonitorProblemTypeChartData: [ 
                {'seriesName': "生产监控异常问题分类", 'seriesData': []}, 
                {'seriesName': "生产监控异常问题top10", 'seriesData': []}, 
                {'seriesName': "生产监控异常问题合计", 'seriesData': 0}
            ],
            saasMonitorProblemCount:0,
        }
    },
    // 计算页面刚加载时候渲染的属性
    computed: {
        getPageWidth: getMainPageWidth
    },
    mounted() {
        this.searchMonitorProvinceList()
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
            if (tableName === 'saasMonitorProblemTopTable' && key === '问题分类') {
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
            echarts.init(document.getElementById('saasMonitorProblemTypeProvinceChart'))
            echarts.init(document.getElementById('saasMonitorProblemProvinceChart'))
            echarts.init(document.getElementById('saasMonitorProblemTypeChart'))
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
                searchValue[i == 0 ? 'beginData' : 'endData'] = year + '-' + month + '-' + day;
            } //结束for，完成日期的拼接
            
            this.saasMonitorProblemTypeProvince(searchValue)
            this.saasMonitorProblemProvince(searchValue)
            this.searchSaaSMonitorProblemByType(searchValue)
        },

        /**
         * 对监控异常的出错的省份列表的后端数据请求
         */
         searchMonitorProvinceList(){
            var searchValue = {} // 存放筛选条件信息
            searchValue['provinceSelected'] = this.provinceSelected
            // 获取年、月、日，进行拼接 
            for (let i = 0; i < this.dateRange.length; i++) {
                var year = this.dateRange[i].getFullYear()
                var month = ('0' + (this.dateRange[i].getMonth() + 1)).slice(-2)
                var day = ('0' + this.dateRange[i].getDate()).slice(-2)
                searchValue[i == 0 ? 'beginData' : 'endData'] = year + '-' + month + '-' + day;
            } 
            this.$http.get(
                '/api/CMC/workrecords/get_saas_monitor_province_list'
            ).then(response =>{
                this.provinceList = response.data["seriesData"]
                if (this.provinceList.length !== 0){
                    this.provinceSelected = this.provinceList[0].region
                }
            }).catch(error =>{
                console.log(error.response.data.message)
                this.$message.error(error.response.data.message)
            })
        },

        /**
         * @param {searchValue} searchValue 搜索参数的字典
         * @description 对第三方出错的出错问题分类关于省份分类的后端数据请求
         */
         async saasMonitorProblemTypeProvince(searchValue) {
            this.$http.get(
                '/api/CMC/workrecords/analysis_saas_monitor_problem_by_type_and_province?beginData=' +
                searchValue['beginData'] +
                '&endData=' +
                searchValue['endData']+
                '&provinceSelected=' +
                searchValue['provinceSelected']
            ).then(response =>{
                this.saasMonitorProblemTypeProvinceChartData = response.data.data
                updateBarChartBasic(document, this.saasMonitorProblemTypeProvinceChartData, '省份生产监控异常分类统计', "category", false, true, 'saasMonitorProblemTypeProvinceChart')
                console.log('update local saasMonitorProblemTypeProvinceChart data: ', this.saasMonitorProblemTypeProvinceChartData)
            }).catch(error =>{
                console.log(error.response.data.message)
                this.$message.error(error.response.data.message)
            })
        },

        /**
         * @param {searchValue} searchValue 搜索参数的字典
         * @description 对第三方出错的关于省份的受理数量的后端数据请求
         */
        async saasMonitorProblemProvince(searchValue) {
            this.$http.get(
                '/api/CMC/workrecords/analysis_saas_monitor_problem_by_province?beginData=' +
                searchValue['beginData'] +
                '&endData=' +
                searchValue['endData']
            ).then(response =>{
                this.saasMonitorProblemProvinceChartData = response.data.data
                updateBarChartBasic(document, this.saasMonitorProblemProvinceChartData, '省份生产监控异常数量统计', "category", false, true, 'saasMonitorProblemProvinceChart')
                console.log('update local saasMonitorProblemProvinceChart data: ', this.saasMonitorProblemProvinceChartData)
            }).catch(error =>{
                console.log(error.response.data.message)
                this.$message.error(error.response.data.message)
            })
        },

        /**
         * @param {searchValue} searchValue 搜索参数的字典
         * @description 对监控异常数量和出错功能的饼状图的后端数据请求
         */
        async searchSaaSMonitorProblemByType(searchValue) {
            this.$http.get(
                '/api/CMC/workrecords/analysis_saas_minitor_problem_by_type?beginData=' +
                searchValue['beginData'] +
                '&endData=' +
                searchValue['endData']
            ).then(response =>{
                this.saasMonitorProblemTypeChartData = response.data.data
                this.saasMonitorProblemCount = this.saasMonitorProblemTypeChartData[2]["seriesData"][0]["value"]
                updatePieChartBasic(document, this.saasMonitorProblemTypeChartData, "生产监控异常问题分类", "saasMonitorProblemTypeChart")
                console.log('update local saasMonitorProblemTypeChart data: ', this.saasMonitorProblemTypeChartData)
            }).catch(error =>{
                console.log(error.response.data.message)
                this.$message.error(error.response.data.message)
            })
        },
    },
};
</script>

<style>
.dropdown-menu {
    max-height: 200px;
    overflow-y: auto;
}

.saasMonitorProblemTypeChart {
  display: inline-block;
}

.saasMonitorProblemTopTable {
  display: inline-block;
}
</style>