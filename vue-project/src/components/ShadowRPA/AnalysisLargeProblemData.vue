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

        <div class="saasLargeProblemTypeProvinceChart" id="saasLargeProblemTypeProvinceChart" :style="{ width: getPageWidth + 'px', height: '400px' }">
        </div>

        <div class="saasLargeProblemProvinceChart" id="saasLargeProblemProvinceChart"
            :style="{ width: getPageWidth + 'px', height: '400px' }">
        </div>

        <div>
            <div class="saasLargeProblemTypeChart" id="saasLargeProblemTypeChart" :style="{ width: getPageWidth * 0.65+ 'px', height: '600px' }">
            </div>
            <div class="saasLargeProblemTopTable" style="width: 35%;">
                <p>{{ saasLargeProblemTypeChartData[2]['seriesName'] }}: <span style="color: red;">{{ saasLargeProblemTypeChartData[2]['seriesData'] }}</span> 次</p>
                <el-table
                :data="saasLargeProblemTypeChartData[1]['seriesData']" 
                :header-cell-style="{fontSize:'14px',background: 'rgb(64 158 255 / 65%)',color:'#696969',}"
                :cell-style="{fontSize: 12 + 'px',}"
                style="width: 100%; margin: auto">
                <el-table-column :label="saasLargeProblemTypeChartData[1].seriesName" align="center">
                    <el-table-column
                    v-for="(item, index) in saasLargeProblemTopTableTitle" :key="index" :prop="item.prop" :label="item.label"
                    :width="columnWidth(item.label, 'saasLargeProblemTopTable')"  align="center">
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
    name: 'AnalysisLargeProblemData',
    data() {
        return {
            // 日期查询范围
            dateRange: [new Date(new Date().getFullYear() + '-01-01'), new Date()],
            // 省份
            provinceList : [],
            provinceSelected: '',
            // 重大故障表头的数据
            saasLargeProblemTopTableTitle: [
                {'prop': "name", "label": "问题分类"},
                {'prop': "value", "label": "次数"},
                {'prop': "percent", "label": "百分比"}
            ],
            saasLargeProblemProvinceChartData: [],
            saasLargeProblemTypeChartData: [ {'seriesName': "", 'seriesData': []}, {'seriesName': "", 'seriesData': []}, {'seriesName': "", 'seriesData': 0} ],
        }
    },
    // 计算页面刚加载时候渲染的属性
    computed: {
        getPageWidth: getMainPageWidth
    },
    mounted() {
        this.searchLargeProblemProvinceList()
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
            if (tableName === 'saasLargeProblemTopTable' && key === '问题分类') {
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
            echarts.init(document.getElementById('saasLargeProblemTypeProvinceChart'))
            echarts.init(document.getElementById('saasLargeProblemProvinceChart'))
            echarts.init(document.getElementById('saasLargeProblemTypeChart'))
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

            this.saasLargeProblemTypeProvince(searchValue)
            this.saasLargeProblemProvince(searchValue)
            this.searchSaaSLargeProblemByType(searchValue)
        },


        /**
         * 对私有化重大故障的省份列表的后端数据请求
         */
         searchLargeProblemProvinceList(){
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
                '/api/CMC/workrecords/analysis_saas_large_problem_province_list?beginData=' +
                searchValue['beginData'] +
                '&endData=' +
                searchValue['endData']
            ).then(response =>{
                this.provinceList = response.data.data[0]["seriesData"]
                this.provinceSelected = this.provinceList[0].region 
            }).catch(error =>{
                console.log(error)
                this.$message.error('错了哦，仔细看错误信息弹窗')
                alert('失败' + error)
            })
        },

        /**
         * @param {searchValue} searchValue 搜索参数的字典
         * @description 对私有化重大故障问题分类关于省份分类的后端数据请求
         */
         async saasLargeProblemTypeProvince(searchValue) {
            try {
                const response = await this.$http.get(
                '/api/CMC/workrecords/analysis_saas_large_problem_by_function_and_province?beginData=' +
                searchValue['beginData'] +
                '&endData=' +
                searchValue['endData']+
                '&provinceSelected=' +
                searchValue['provinceSelected']
                )
                this.saasLargeProblemTypeProvinceChartData = response.data.data
                updateBarChartBasic(document, this.saasLargeProblemTypeProvinceChartData, '省份私有化重大故障类型统计', "category", false, true, 'saasLargeProblemTypeProvinceChart')
                
                // 因为重大故障这个x轴的标签有的过于长，就算换行显示也还是会乱在一起。
                // 所以进行判断，x轴的多于10个标签的正常来说换行也不能解决问题，所以进行斜着显示，并且将换行清除和grid进行调整（否则末尾的标签斜着会溢出图表所在区域）。
                // 如果小于10个标签，那么原来update函数中就会自己判断是否正常显示或者换行显示。
                let saasLargeProblemTypeProvinceChart = echarts.getInstanceByDom(document.getElementById("saasLargeProblemTypeProvinceChart"))
                let xAxisData = this.saasLargeProblemTypeProvinceChartData[0].seriesData.map(item => item.x)
                xAxisData.length > 10 && saasLargeProblemTypeProvinceChart && saasLargeProblemTypeProvinceChart.setOption({
                    grid: {
                        left: '3%',
                        right: '5%',
                        top: '20%',
                        bottom: '10%',
                        containLabel: true
                    },
                    xAxis : {
                        data: xAxisData,
                        axisLabel: {  
                            interval:0,      //坐标轴刻度标签的显示间隔(在类目轴中有效) 0:显示所有  1：隔一个显示一个 :3：隔三个显示一个...
                            rotate:-20    //标签倾斜的角度，显示不全时可以通过旋转防止标签重叠（-90到90）
                        }
                    }
                })

                console.log('update local saasLargeProblemTypeProvinceChart data: ', this.saasLargeProblemTypeProvinceChartData)

            } catch (error) {
                console.log(error)
                this.$message.error('错了哦，仔细看错误信息弹窗')
                alert('失败' + error)
            }
        },

        /**
         * @param {searchValue} searchValue 搜索参数的字典
         * @description 对重大故障的关于省份的受理数量的后端数据请求
         */
        async saasLargeProblemProvince(searchValue) {
            try {
                const response = await this.$http.get(
                '/api/CMC/workrecords/analysis_saas_large_problem_by_province?beginData=' +
                searchValue['beginData'] +
                '&endData=' +
                searchValue['endData']
                )
                this.saasLargeProblemProvinceChartData = response.data.data
                updateBarChartBasic(document, this.saasLargeProblemProvinceChartData, '省份私有化重大故障数量统计', "category", false, true, 'saasLargeProblemProvinceChart')
                console.log('update local saasLargeProblemProvinceChart data: ', this.saasLargeProblemProvinceChartData)

            } catch (error) {
                console.log(error)
                this.$message.error('错了哦，仔细看错误信息弹窗')
                alert('失败' + error)
            }
        },

        /**
         * @param {searchValue} searchValue 搜索参数的字典
         * @description 对重大事故数量和出错功能的饼状图的后端数据请求
         */
        async searchSaaSLargeProblemByType(searchValue) {
            try {
                const response = await this.$http.get(
                '/api/CMC/workrecords/analysis_saas_large_problem_by_function?beginData=' +
                searchValue['beginData'] +
                '&endData=' +
                searchValue['endData']
                )
                this.saasLargeProblemTypeChartData = response.data.data
                updatePieChartBasic(document, this.saasLargeProblemTypeChartData, "私有化重大故障问题分类", "saasLargeProblemTypeChart")
                console.log('update local saasLargeProblemTypeChart data: ', this.saasLargeProblemTypeChartData)

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
.saasLargeProblemTypeChart {
  display: inline-block;
}

.saasLargeProblemTopTable {
  display: inline-block;
}
</style>