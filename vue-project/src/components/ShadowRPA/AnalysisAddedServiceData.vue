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
import { updateBarChartBasic } from '@/utils/echartBasic'

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
        /**
         * 获取主页面宽度
         */
        getPageWidth: function () {
            // windows.screen.width返回屏幕宽度，减去侧边栏240px,减去container模型左右padding各20px和margin-right的10px,
            // 减去主页面各自15px的padding, 减去不知道那里vue自己设的30px, 减去主页面内元素和滚动条保持距离的padding-right的10px,
            return (window.screen.width - 240 - 20 * 2 - 10 - 15 * 2 - 30 - 10)
        },
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
         * 当查询之后，数据更新，更新重大事故数量和出错功能的饼状图的数据
         */
         updateSaaSAddedServiceTypeChart(chartData, chartTitle, chartElementId){
            let chart = echarts.getInstanceByDom(document.getElementById(chartElementId))

            let option = {
                title: {
                text: chartTitle,
                left: 'left'
                },
                tooltip: {
                trigger: 'item',
                formatter: '{a} <br/>{b} : {c} ({d}%)'
                },
                series: [
                {
                    name: chartData[0].seriesName,
                    type: 'pie',
                    radius: '55%',
                    data: chartData[0].seriesData,
                    top: '7%',
                    labelLine: {
                    length: 15,
                    maxSurfaceAngle: 80
                    },
                    label: {
                    alignTo: 'edge',
                    formatter: '{b|{b}：}{c}次 {per|{d}%}  ',
                    minMargin: 5,
                    lineHeight: 15,
                    // 这个配置不知道为什么，给的值越大，edge distance其实越小
                    edgeDistance: 10,
                    rich: {
                        b: {
                        color: '#4C5058',
                        fontSize: 12,
                        fontWeight: 'bold',
                        lineHeight: 25
                        },
                        per: {
                        color: '#fff',
                        backgroundColor: '#4C5058',
                        padding: [3, 4],
                        // borderRadius: 4
                        }
                    }
                    },
                    // 给标签线设置格式
                    labelLayout: function (params) {
                    // 通过标签魔性labelRect的x，查看是在这张图左边还是右边 （不能使用params.label.x直接看label的文字的坐标，不知道为什么直接整个回调所有设置失效）
                    const isLeft = params.labelRect.x < chart.getWidth() / 2;
                    const points = params.labelLinePoints;
                    // 更新水平方向的标签线的末尾坐标，看是左边的标签还是右边的标签，如果是右边的标签的话就取到标签的x值也就是标签最靠左的点然后加上标签宽度
                    points[2][0] = isLeft ? params.labelRect.x : params.labelRect.x + params.labelRect.width;
                    // 更新竖直方向的标签线的末尾坐标，因为想要label显示在线上方，所以加上label的高度。
                    points[1][1] = params.labelRect.y+params.labelRect.height
                    points[2][1] = params.labelRect.y+params.labelRect.height
                    return {
                        labelLinePoints: points
                    };
                    },
                    emphasis: {
                    itemStyle: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                    }
                }
                ]
            };

            chart&&chart.setOption(option, true)
            console.log("updated "+chartElementId+" echart: ", chart)
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
         * 对监控异常的出错的省份列表的后端数据请求
         */
         searchAddedServiceProvinceList(){
            var searchValue = {} // 存放筛选条件信息
            searchValue['provinceSelected'] = this.provinceSelected
            // 获取年、月、日，进行拼接 
            for (let i = 0; i < this.dateRange.length; i++) {
                var year = this.dateRange[i].getFullYear()
                var month = ('0' + (this.dateRange[i].getMonth() + 1)).slice(-2)
                var day = ('0' + this.dateRange[i].getDate()).slice(-2)
                if (i == 0) {
                    // 构建格式化后的日期字符串
                    var beginData = year + '-' + month + '-' + day
                    searchValue['beginData'] = beginData
                }
                if (i == 1) {
                    var endData = year + '-' + month + '-' + day
                    searchValue['endData'] = endData
                }
            } 
            this.$http.get(
                '/api/CMC/workrecords/analysis_saas_added_service_province_list?beginData=' +
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
         * @description 对第三方出错的出错问题分类关于省份分类的后端数据请求
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
                updateBarChartBasic(document, this.saasAddedServiceTypeProvinceChartData, '省份生产监控异常分类统计', "category", false, 'saasAddedServiceTypeProvinceChart')
                console.log('update local saasAddedServiceTypeProvinceChart data: ', this.saasAddedServiceTypeProvinceChartData)

            } catch (error) {
                console.log(error)
                this.$message.error('错了哦，仔细看错误信息弹窗')
                alert('失败' + error)
            }
        },

        /**
         * @param {searchValue} searchValue 搜索参数的字典
         * @description 对第三方出错的关于省份的受理数量的后端数据请求
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
                updateBarChartBasic(document, this.saasAddedServiceProvinceChartData, '省份增值服务统计', "category", false, 'saasAddedServiceProvinceChart')
                console.log('update local saasAddedServiceProvinceChart data: ', this.saasAddedServiceProvinceChartData)

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
        async searchSaaSAddedServiceByType(searchValue) {
            try {
                const response = await this.$http.get(
                '/api/CMC/workrecords/analysis_saas_added_service_by_function?beginData=' +
                searchValue['beginData'] +
                '&endData=' +
                searchValue['endData']
                )
                this.saasAddedServiceTypeChartData = response.data.data
                this.updateSaaSAddedServiceTypeChart(this.saasAddedServiceTypeChartData, "增值服务分类", "saasAddedServiceTypeChart")
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