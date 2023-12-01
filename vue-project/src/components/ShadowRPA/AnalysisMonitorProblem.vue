<template>
    <div>
        <div style="margin: 15px 0">
            <span class="demonstration" style="margin-left: 15px;">省份： </span>
            <el-select v-model = "provinceSelected" placeholder = "请选择省份" style="width: 120px;">
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
                <p>{{ saasMonitorProblemTypeChartData[2]['seriesName'] }}: <span style="color: red;">{{ saasMonitorProblemTypeChartData[2]['seriesData'] }}</span> 次</p>
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
            echarts.init(document.getElementById('saasMonitorProblemProvinceChart'))
            echarts.init(document.getElementById('saasMonitorProblemTypeChart'))
            echarts.init(document.getElementById('saasMonitorProblemTypeProvinceChart'))
        },

        /**
         * @param barChartData 整个图的数据数组
         * @param barChartTitle 这张图的标题
         * @param xAxisType x轴的坐标类型，有date，value，category等等
         * @param xAxisLabelNewLine 因为有些时候，x轴的坐标分类太多，比如当有30个以上的category的时候，导致x轴的有些标签会缺失，这个输入如果为true,会将偶数的label换行形成更多空间展示
         * @param chartElementId 对应的要更新的图表元素id
         * @description 当查询之后，数据更新，根据新的数据更新柱状图的基础配置。
         * 整个图的数据是一个大数组，里面包含的每个字典是：有属性seriesName, data。这里seriesName是该series的名字，data是该series的数据。
         * data是一个数组，里面同样也是多个字典，每个字典代表着一个数据点，格式为 {‘x’: "xxx", "y": "xxx", "aaa":"aaa", "bbb":"bbb"}
         * x和y的值是用于对应图的x和y轴的值，剩下的aaa，bbb等是其他可能多的需要添加的数据标签，但是再本基础配置方法中不做处理，只做x和y的对应。
         * xAxis的type为传入的参数，有date，value，category等等，yAxis的type默认为value,因为y轴一般是数值。
         */
        updateBarChartBasic(barChartData, barChartTitle, xAxisType, xAxisLabelNewLine, chartElementId) {
        // 拿到x轴的数据
        let xAxisData = barChartData[0].seriesData.map(item => item.x)
        // 将如果所有项都是0的x轴的值去掉
        let removeList = []
        xAxisData.forEach((item) => {
            let count = 0
            barChartData.forEach(({ seriesData }) => { count = (seriesData.find(ele => ele.x === item).y === 0) ? count + 1 : count })
            if (count === barChartData.length) removeList.push(item)
        })
        xAxisData = xAxisData.filter(item => !removeList.includes(item))

        let option = {
            title: {
                top: '1%',
                left: '5%',
                text: barChartTitle,
                left: 'left'
            },
            tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            }
            },
            legend: {
            top: '8%',
            },
            grid: {
            left: '3%',
            right: '3%',
            top: '23%',
            bottom: '15%',
            containLabel: true
            },
            xAxis: [
            {
                type: xAxisType,
                axisLabel: { interval: 0 },
                data: xAxisData
            }
            ],
            yAxis: [
            {
                type: 'value'
            }
            ],
            series: []
        };

        // 根据数据对图标添加series
        this.normalBarChartAddingSeries(barChartData, option)

        // 看看是否要给x轴数据添加换行
        xAxisData = (xAxisLabelNewLine) ? xAxisData.map((item, index) => (index % 2 === 0) ? item : '\n' + item) : xAxisData
        option.xAxis[0].data = xAxisData

        let chart = echarts.getInstanceByDom(document.getElementById(chartElementId))
        chart && chart.setOption(option, true)

        console.log("updated " + chartElementId + " echart : ", chart)
        },

        /**
         * 将柱状图的数组信息循环添加进入柱状图的series中
         * @param {barChartData} barChartData 后端返回的包含柱状图所有信息的一个数组
         * @param {option} option 柱状图的option
         */
        normalBarChartAddingSeries(barChartData, option) {
        // 指定了柱子的15种颜色，因为不设置的话echarts默认超过9个颜色会开始循环，所以扩大一点，变成15个颜色开始循环
        let colors = ["#5470C6", "#91CC75", "#FAC858", "#EE6666", "#73C0DE", "#3BA272", "#fc8452", "#a26dba", "#ea7ccc", "#ffe630", "#00A0AF", "#DB643E", "#EA8D89", "#F4B2E5", "#F03A6A"]
        for (let i = 0; i < barChartData.length; i++) {
            let series_1 = {
            name: barChartData[i].seriesName,
            type: 'bar',
            barMaxWidth: 30,
            emphasis: {
                focus: 'series'
            },
            // data: barChartData[i].seriesData.map(item=>item.y),
            data: barChartData[i].seriesData.filter((item) => option.xAxis[0].data.includes(item.x)).map(item => item.y),
            itemStyle: {
                color : colors[i%colors.length]
            },
            label: {
                // 设置柱形图的数值
                show: true,
                position: 'top',
                align: 'center',
                // formatter: function (params){
                //   return (params.value===0)?"":params.value+"次"
                // },
                formatter: '{c|{c}}次',
                rich: {
                c: {
                    // color: '#4C5058',
                    fontSize: 10,
                },
                }
            },
            }
            option.series.push(series_1)
        }
        },

        /**
         * 当查询之后，数据更新，更新重大事故数量和出错功能的饼状图的数据
         */
         updateSaaSMonitorProblemTypeChart(chartData, chartTitle, chartElementId){
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
                if (i == 0) {
                    // 构建格式化后的日期字符串
                    var beginData = year + '-' + month + '-' + day
                    searchValue['beginData'] = beginData
                }
                if (i == 1) {
                    var endData = year + '-' + month + '-' + day
                    searchValue['endData'] = endData
                }
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
                '/api/CMC/workrecords/analysis_saas_monitor_province_list?beginData=' +
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
         async saasMonitorProblemTypeProvince(searchValue) {
            try {
                const response = await this.$http.get(
                '/api/CMC/workrecords/analysis_saas_monitor_problem_by_function_and_province?beginData=' +
                searchValue['beginData'] +
                '&endData=' +
                searchValue['endData']+
                '&provinceSelected=' +
                searchValue['provinceSelected']
                )
                this.saasMonitorProblemTypeProvinceChartData = response.data.data
                this.updateBarChartBasic(this.saasMonitorProblemTypeProvinceChartData, '省份生产监控异常分类统计', "category", false, 'saasMonitorProblemTypeProvinceChart')
                console.log('update local saasMonitorProblemTypeProvinceChart data: ', this.saasMonitorProblemTypeProvinceChartData)

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
        async saasMonitorProblemProvince(searchValue) {
            try {
                const response = await this.$http.get(
                '/api/CMC/workrecords/analysis_saas_monitor_problem_by_province?beginData=' +
                searchValue['beginData'] +
                '&endData=' +
                searchValue['endData']
                )
                this.saasMonitorProblemProvinceChartData = response.data.data
                this.updateBarChartBasic(this.saasMonitorProblemProvinceChartData, '省份生产监控异常数量统计', "category", false, 'saasMonitorProblemProvinceChart')
                console.log('update local saasMonitorProblemProvinceChart data: ', this.saasMonitorProblemProvinceChartData)

            } catch (error) {
                console.log(error)
                this.$message.error('错了哦，仔细看错误信息弹窗')
                alert('失败' + error)
            }
        },


        /**
         * @param {searchValue} searchValue 搜索参数的字典
         * @description 对监控异常数量和出错功能的饼状图的后端数据请求
         */
        async searchSaaSMonitorProblemByType(searchValue) {
            try {
                const response = await this.$http.get(
                '/api/CMC/workrecords/analysis_saas_minitor_problem_by_function?beginData=' +
                searchValue['beginData'] +
                '&endData=' +
                searchValue['endData']
                )
                this.saasMonitorProblemTypeChartData = response.data.data
                this.updateSaaSMonitorProblemTypeChart(this.saasMonitorProblemTypeChartData, "生产监控异常问题分类", "saasMonitorProblemTypeChart")
                console.log('update local saasMonitorProblemTypeChart data: ', this.saasMonitorProblemTypeChartData)

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