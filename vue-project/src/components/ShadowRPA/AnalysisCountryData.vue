<template>
    <div>
        <div style="margin: 15px 0">
            <div style="margin-bottom: 10px;">
                <span class="demonstration">省份： </span>
                <el-select v-model = "provinceSelected" placeholder = "请选择省份" style="width: 120px;" :clearable="true">
                    <el-option v-for="(item,index) in this.provinceList" :key="index" :label="item" :value="item"></el-option>
                </el-select>
                <span class="demonstration" style="margin-left: 15px;">时间范围： </span>
                <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期"
                    end-placeholder="结束日期">
                </el-date-picker>
                <el-button type="primary" @click="search">查询</el-button>
            </div>
            <!-- 功能分类 -->
            <div>
                <div style="margin-bottom: 10px;">
                    <span class="demonstration">业务分类： </span>
                    <el-checkbox-group v-model="businessSelected" @change="businessCheckBoxChange"
                        style="display: inline-block;">
                        <el-checkbox v-for="(item, index) in businessOptions" :key="index" :label="item">{{ item
                        }}</el-checkbox>
                    </el-checkbox-group>
                </div>

                <div>
                    <span class="demonstration">功能分类： </span>
                    <el-checkbox-group v-model="functionSelected" style="display: inline-block;">
                        <el-checkbox v-for="(item, index) in functionOptions[this.businessSelected]" :key="index"
                            :label="item">{{
                                item }}</el-checkbox>
                    </el-checkbox-group>
                </div>
            </div>
        </div>
        <div style="height: 10px;"></div>
        <div style="height: 600px;">
            <div class="saasChinaMapShow">
                <div id = "saasFunctionTypeBarChart" class="saasFunctionTypeBarChart" :style="{ width: getPageWidth * 0.275 + 'px', height: '200px'}"></div>
                <div id = "saasProblemTypeBarChart" class="saasProblemTypeBarChart" :style="{ width: getPageWidth * 0.275 + 'px', height: '200px'}"></div>
                <div id = "saasMonitorProblemTypeBarChart" class="saasMonitorProblemTypeBarChart" :style="{ width: getPageWidth * 0.275 + 'px', height: '200px'}"></div>
            </div>
            <div class="saasChinaMapShow">
                <div id="saasProblemChinaMap" class="saasProblemChinaMap" :style="{ width: getPageWidth * 0.45 + 'px', height: '430px'}"></div>
                <div id = "saasSoftVersionAmountBarChart" class="saasSoftVersionAmountBarChart" :style="{ width: getPageWidth * 0.45 + 'px', height: '177px'}"></div>
            </div>
            <div class="saasChinaMapShow" style="width: 27.2%;">
                <!-- 因为饼图没有grid设置，然后data会顶到底部，所以需要一个padding用于和下面图形进行分开-->
                <div id = "saasAgencyTypePieChart" class="saasAgencyTypePieChart" :style="{ width: getPageWidth * 0.275 + 'px', height: '200px', padding: '0 0 10px 0'}"></div>
                <div id = "saasLargeProblemTypeBarChart" class="saasLargeProblemTypeBarChart" :style="{ width: getPageWidth * 0.275 + 'px', height: '200px'}"></div>
                <div style="height: 190px;">
                    <el-row>
                        <!-- line-height 是为了让竖直居中，计算方法为外部div的height/(col的数量/2) * 2 -->
                        <el-col v-for="(row, rowIndex) in saasCountrySummaryData" :key="rowIndex" style="width: 50%; text-align: center; line-height: 31px;">
                            <el-row class="threeDText">{{ row.name }}</el-row>
                            <el-row class="sevenDital">{{ row.value }}</el-row>
                        </el-col>
                    </el-row>
                </div>
            </div>
        </div>
        
        <!-- 因为map是通过geo控制大小的，并没有办法使用grid来控制，所以map的高度无法控制，只能在那个div下面配上一个空间进行和下面图标的分割 -->
        <div style="height: 40px;"></div>

        <div class="saasProvinceAndFunctionChart normalChartSize" id="saasProvinceAndFunctionChart"></div>
        <div class="saasProvinceAndFunctionChartSplit" id="saasProvinceAndFunctionChartSplit">
            <!-- 因为省份和功能会产生太多柱子，所以对省份进行一个切割，分成多张图来展现，注意，v-for这边生成的i是从1开始，所以id的末尾是1不是0 -->
            <div v-for="i in provinceSplitNum" :class="'saasProvinceAndFunctionChart' + i" :id="'saasProvinceAndFunctionChart' + i"></div>
        </div>
        <div class="saasProvinceAndAgencyChart" id="saasProvinceAndAgencyChart" :style="{ width: getPageWidth + 'px', height: '400px' }"></div>
        <div class="saasProblemMonthChart" id="saasProblemMonthChart" :style="{ width: getPageWidth+ 'px', height: '400px' }"></div>
        <div class="saasVersionTrendChart" id="saasVersionTrendChart" :style="{ width: getPageWidth+ 'px', height: '400px' }"></div>
    </div>
</template>
  
<script>
import { getMainPageWidth } from '@/utils/layoutUtil'
import { updateBarChartBasic, updatePieChartBasic} from '@/utils/echartBasic'

import * as echarts from 'echarts'; // 引入 ECharts 库, 该项目安装的是5.4.3版本的echarts
// 这个chinaMap.json是有完全版本的是从 https://datav.aliyun.com/portal/school/atlas/area_selector 进行获取的
// 仿照从 https://www.cnblogs.com/CandyDChen/p/13889761.html 弄下来的格式进行优化 （因为它的数据可能是筛选的数据，边境线显示太过广泛，显示不完全，台湾周围的岛也没有）
// 优化显示（南海群岛的去除，省份命名的缩减，省份label显示的居中，地图size的放大）
import chinaMap from "@/assets/json/chinaMap.json";

export default {
    name: 'AnalysisCountryData',
    data() {
        return {
            chinaMap: null,
            // 日期查询范围
            dateRange: [new Date(new Date().getFullYear() + '-01-01'), new Date()],
            // 业务选择
            businessOptions: ['日常业务', '其他业务'],
            businessSelected: [],
            // 功能选择
            functionOptions: {
                "日常业务": ["开票功能", "收缴业务", "核销功能", "打印功能", "报表功能", "票据管理", "通知交互", "反算功能", "数据同步"],
                "其他业务": ["增值服务", "单位开通", "license重置", "安全漏洞"],
            },
            functionSelected: '',
            provinceSelected : "",
            provinceList : [],

            // 将省份和出错功能对比的柱形图分割成几个子图
            provinceSplitNum: 2,
            // 省份与出错功能柱状图的子集的图的收缩state
            provinceSplitState : false,

            chinaMapProvinceSaaSProblemData: [],
            saasFunctionTypeBarChartData : [],
            saasProblemTypeBarChartData : [],
            saasMonitorProblemTypeBarChartData : [],
            saasSoftVersionAmountBarChartData : [],
            saasAgencyTypePieChartData : [],
            saasLargeProblemTypeBarChartData : [],
            saasCountrySummaryData: [],
            saasProvinceBarChartData: [],
            saasProvinceProblemAmountMax: 0, //该值用来对省份子集的y轴大小做一个统一，否则y轴会根据里面的数据自适应缩放大小
            saasProvinceAndAgencyChartData: [],
            saasProblemMonthChartData: [],
            saasVersionBarChartData: [],
        }
    },
    // 计算页面刚加载时候渲染的属性
    computed: {
        getPageWidth: getMainPageWidth
    },
    mounted() {
        this.businessSelected.push(this.businessOptions[0]);
        this.functionSelected = this.functionOptions[this.businessSelected].slice(0, 3);
        this.provinceList = ['北京','天津','上海','重庆','河北','山西','辽宁','吉林', '云南', '新疆', '广西', '甘肃', '内蒙古', '陕西', '西藏', 
                       '四川', '宁夏', '黑龙江','江苏','浙江','安徽','福建','江西','山东','河南','湖北','湖南','广东','海南', '贵州', '青海', 
                       '台湾', '香港', '澳门'];
        this.provinceList.unshift("全国");
        this.provinceSelected = this.provinceList[0];
        // 初始化中国的地图的数据，从本地配置文件中读取
        echarts.registerMap("china", { geoJSON: chinaMap });
        // 进行图的配置
        this.drawCharts()
    },
    methods: {
        /**
         * 业务类型的checkbox单选功能
         * @param {*} value 
         */
        businessCheckBoxChange(value) {
            if (this.businessSelected.length > 1) {
                this.businessSelected.splice(0, 1)
            }
            this.functionSelected = this.functionOptions[this.businessSelected];
        },

        // echarts各类图表的init
        drawCharts() {
            this.initChinaMap()

            // 其他图表的init
            echarts.init(document.getElementById('saasFunctionTypeBarChart'))
            echarts.init(document.getElementById('saasProblemTypeBarChart'))
            echarts.init(document.getElementById('saasMonitorProblemTypeBarChart'))
            echarts.init(document.getElementById('saasSoftVersionAmountBarChart'))
            echarts.init(document.getElementById('saasAgencyTypePieChart'))
            echarts.init(document.getElementById('saasLargeProblemTypeBarChart'))
            echarts.init(document.getElementById('saasProvinceAndFunctionChart'))
            echarts.init(document.getElementById('saasProvinceAndAgencyChart'))
            echarts.init(document.getElementById('saasProblemMonthChart'))
            echarts.init(document.getElementById('saasVersionTrendChart'))
        },

        /**
         * 对中国地图的echart做一个初始化
         */
        initChinaMap(){
            // 在 mounted 钩子中初始化 china map echarts 实例，并获取容器
            this.saasProblemChinaMap = echarts.init(document.getElementById('saasProblemChinaMap'))
            // ECharts 配置项
            const option = {
                title : {
                    show: true,
                    text: '全国受理问题分布',
                    left: '2%',
                    top: '2%',
                    textStyle: {
                        fontSize: 18
                    }
                },
                tooltip: {
                    triggerOn: 'mousemove',
                    formatter: function (param) {
                        // 通过param.data来获取鼠标悬浮的那个数据点的信息
                        return `省份: ${param.data.name}<br/>单位开通: ${param.data.agencyValue}<br/>受理次数: ${param.data.value}`
                    }
                },
                // geo为地理坐标系组件，用于地图的绘制，支持在地理坐标系上绘制散点图，线集。
                geo: {
                    map: 'china', // 使用 registerMap 注册的地图名称。
                    zoom: 1.2,
                    label: {
                        show: true,
                    }
                },
                series: [
                    {
                        name: "",
                        type: 'map',
                        geoIndex: 0,
                        data: []
                    }
                ]
            }
            // 使用刚指定的配置项和数据显示图表
            this.saasProblemChinaMap.setOption(option);
            // 因为要在on的click的回调函数中调用这个vue的searchSaaSCountryRelevantData方法，直接使用this会指向saasProblemChinaMap，所以用that暂存
            var that = this
            // 给map设置点击时间，用于切换省份使用
            this.saasProblemChinaMap.on("click", function (params) { //点击事件
                console.log(params.name, ' 我被点击了 ',params)
                // 判断是否toggle省份，因为echart的map自带的点击一个省份会亮起，再点击一次会取消亮起，那么也就模仿为点击一次search该省份，再点击一次返回search全国
                that.provinceSelected = (that.provinceSelected === params.name) ? "全国" : params.name
                // 获取省份对应的图表统计
                that.searchSaaSCountryRelevantData()
            });
        },

        /**
         * 当查询之后，数据更新，更新省份受理与单位数量对比的省份数据柱状图和单位数量的折线数据更新
         */
        updateSaaSProvinceAndAgencyBarChart(barChartData, barChartTitle, xAxisType, xAxisLabelNewLine, chartElementId) {
            let xAxisData = this.saasProvinceAndAgencyChartData[0].seriesData.map(item => item.x)
            let colors = ["#5470C6", "#FAC858", "#EE6666"];
            let option = {
                color: colors,
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
                        type: 'value',
                        name: '受理数量',
                        alignTicks: true,
                        position: 'left',
                        axisLine: {
                            show: true,
                            lineStyle: {
                                color: colors[0]
                            }
                        },
                    },
                    {
                        type: 'value',
                        name: '单位数量',
                        position: 'right',
                        alignTicks: true,
                        axisLine: {
                            show: true,
                            lineStyle: {
                                color: colors[2]
                            }
                        },
                    }
                ],
                series: [
                    {
                        name: barChartData[0].seriesName,
                        type: 'bar',
                        // 这里可以直接map把y的值取出来，因为这里就一组series，y为0的x过滤就不会存在，xAxis还是原来的不会有x的值被去除，使用这里并不需要让y再去对应xAxis的进行过滤
                        data: barChartData[0].seriesData.map(item => item.y),
                    },
                    {
                        name: barChartData[1].seriesName,
                        type: 'bar',
                        yAxisIndex: 0,
                        data: barChartData[1].seriesData.map(item => item.y),
                    },
                    {
                        name: barChartData[2].seriesName,
                        type: 'line',
                        yAxisIndex: 1,
                        data: barChartData[2].seriesData.map(item => item.y),
                    }
                ]
            }

            // 看看是否要给x轴数据添加换行
            xAxisData = (xAxisLabelNewLine) ? xAxisData.map((item, index) => (index % 2 === 0) ? item : '\n' + item) : xAxisData
            option.xAxis[0].data = xAxisData

            let chart = echarts.getInstanceByDom(document.getElementById(chartElementId))
            // 现在是添加属性，所以不用replace设成true，直接setOption就行
            chart && chart.setOption(option, true)

            console.log("updated saasProvinceAndAgencyChart echart: ", chart)
        },

        /**
         * 对省份子集的图进行update数据
         */
        updateSaasProvinceAndFunctionSplitChart(){
            let interval = this.saasProvinceBarChartData[0]["seriesData"].length / this.provinceSplitNum
            // 要分成几张图的数据，进行遍历循环，给柱状图添加数据。
            for (let i = 0; i < this.provinceSplitNum; i++) {
                const ele = document.getElementById('saasProvinceAndFunctionChart' + (i + 1))
                ele.classList.add('normalChartSize')
                echarts.init(ele)
                let splitData = []
                this.saasProvinceBarChartData.forEach((item) => { splitData.push({ seriesName: item.seriesName, seriesData: item.seriesData.slice(i * interval, (i + 1) * interval) }) })
                // 将数据注入柱状图内，i+1是因为元素在使用v-for生成的时候，v-for的i是从1开始，这里是0开始，所以使用i+1来获取相同的id
                updateBarChartBasic(document, splitData, 'SaaS省份三线受理统计(子集' + (i + 1) + ')', "category", false, true, 'saasProvinceAndFunctionChart' + (i + 1))
                let chart = echarts.getInstanceByDom(document.getElementById('saasProvinceAndFunctionChart' + (i + 1)))
                chart && chart.setOption({
                    yAxis: {
                        type: "value",
                        max: Math.ceil(this.saasProvinceProblemAmountMax / 10) * 10
                    }
                })

                // 判断是否要隐藏子集
                if (!this.provinceSplitState && !ele.classList.contains('hidden')) ele.classList.add('hidden')
            }
        },

        async search() {
            var searchValue = {} // 存放筛选条件信息
            searchValue['functionName'] = this.functionSelected.toString()
            searchValue['provinceSelected'] = this.provinceSelected
            // 获取年、月、日，进行拼接
            for (let i = 0; i < this.dateRange.length; i++) {
                var year = this.dateRange[i].getFullYear()
                var month = ('0' + (this.dateRange[i].getMonth() + 1)).slice(-2)
                var day = ('0' + this.dateRange[i].getDate()).slice(-2)
                searchValue[(i==0)?"beginData":"endData"] = year + "-" + month + "-" + day;
            }

            this.searchSaaSCountryData(searchValue)
            this.searchSaaSCountryRelevantData()
            this.searchSaaSFunctionByProvince(searchValue)
            this.searchSaaSProblemByProvinceAgency(searchValue)
            this.searchSaaSProblemByMonth(searchValue)
            this.searchSaaSVersionUpgradeTrend(searchValue)
        },

        /**
         * 搜索给ChinaMap使用的数据
         * @param {*} searchValue 
         */
        async searchSaaSCountryData(searchValue) {
            try {
                const response = await this.$http.get(
                    '/api/CMC/workrecords/analysis_saas_problem_by_country?beginData=' +
                    searchValue['beginData'] +
                    '&endData=' +
                    searchValue['endData']
                )
                // 默认后端给的数据，第一个是map的数据
                // 拿到map的数据
                this.chinaMapProvinceSaaSProblemData = response.data.data
                // 把valueMax的值取出来
                let valueMax = this.chinaMapProvinceSaaSProblemData.pop()
                let saasProblemChinaMap = echarts.getInstanceByDom(document.getElementById("saasProblemChinaMap"))
                // 现在是添加属性，所以不用replace设成true，直接setOption就行
                saasProblemChinaMap && saasProblemChinaMap.setOption({
                    visualMap: {//左下角的渐变颜色条
                        min: 0,
                        max: valueMax.valueMax,
                        left: 'left',
                        top: 'bottom',
                        text: [valueMax.valueMax + "", 0 + ""],
                        inRange: {
                            color: ['#FCF7F6', '#FD2C05 ']
                        },
                        padding : [ 0, 0, 20, 15],
                        show: true
                    },
                    series: [
                        {
                            name: this.chinaMapProvinceSaaSProblemData[0]["seriesName"],
                            type: 'map',
                            geoIndex: 0,
                            data: this.chinaMapProvinceSaaSProblemData[0]["seriesData"]
                        }
                    ]
                })
                console.log('update local map data: ', this.chinaMapProvinceSaaSProblemData)

            } catch (error) {
                console.log(error)
                this.$message.error('错了哦，仔细看错误信息弹窗')
                alert('失败' + error)
            }
        },

        /**
         * 对地图周围的展示的map进行搜索，展现出省份里面的具体受理的统计图表情况。
         */
        async searchSaaSCountryRelevantData(){
            try{

                let searchValue = {}
                searchValue["province"] = this.provinceSelected
                // 获取年、月、日，进行拼接
                for (let i = 0; i < this.dateRange.length; i++) {
                    var year = this.dateRange[i].getFullYear()
                    var month = ('0' + (this.dateRange[i].getMonth() + 1)).slice(-2)
                    var day = ('0' + this.dateRange[i].getDate()).slice(-2)
                    searchValue[(i==0)?"beginData":"endData"] = year + "-" + month + "-" + day;
                }

                const response = await this.$http.get(
                    '/api/CMC/workrecords/analysis_saas_problem_by_country_region?beginData=' +
                    searchValue['beginData'] +
                    '&endData=' +
                    searchValue['endData'] +
                    '&province=' +
                    searchValue['province']
                )

                // 这里是因为环绕在地图周围，所以size比较小，进行边距和轴标签的特殊设置
                let smallSizeBarChartOption = {
                    legend: {data: []},
                    grid: {
                        left: '3%',
                        right: '3%',
                        top: '23%',
                        bottom: '7%',
                    },
                    xAxis : {
                        axisLabel: {
                            textStyle: {
                                fontSize: "11",
                            },
                        },
                    },
                    yAxis : {
                        axisLabel: {
                            textStyle: {
                                fontSize: "11",
                            },
                        },
                    },
                }

                // size较小的横向柱状图的设置，将标签设在内部并且靠左对齐
                let smallSizeHorizontalBarChartOption = {
                    legend: {data: []},
                    grid: {
                        left: '3%',
                        right: '3%',
                        top: '20%',
                        bottom: '10%',
                    },
                    series: {
                        label: {
                            show: true,
                            formatter: '{b|{b}: {c}}次',
                            // 横向柱状图，将标签设置在柱状内部，并且靠左对齐，padding是为了默认靠左对齐离y轴太近。
                            position: 'insideLeft',
                            align : 'left',
                            padding : [0, -12, 0, 12],
                        },
                    },
                    yAxis: {
                        // 将y轴标签去除，因为太长了，想展示在柱状内部
                        axisLabel: { show: false },
                    },
                }

                // 拿到saasFunctionType柱状图的数据
                this.saasFunctionTypeBarChartData = response.data.data[0]
                updateBarChartBasic(document, this.saasFunctionTypeBarChartData, this.saasFunctionTypeBarChartData[0]["seriesName"], "category", false, true, 'saasFunctionTypeBarChart')
                let saasFunctionTypeBarChart = echarts.getInstanceByDom(document.getElementById("saasFunctionTypeBarChart"))
                saasFunctionTypeBarChart && saasFunctionTypeBarChart.setOption(smallSizeBarChartOption)

                // 拿到saasProblemType柱状图的数据
                this.saasProblemTypeBarChartData = response.data.data[1]
                updateBarChartBasic(document, this.saasProblemTypeBarChartData, this.saasProblemTypeBarChartData[0]["seriesName"], "category", false, true, 'saasProblemTypeBarChart')
                let saasProblemTypeBarChart = echarts.getInstanceByDom(document.getElementById("saasProblemTypeBarChart"))
                saasProblemTypeBarChart && saasProblemTypeBarChart.setOption(smallSizeBarChartOption)
                
                // 拿到saasMonitorProblemType柱状图的数据
                this.saasMonitorProblemTypeBarChartData = response.data.data[2]
                updateBarChartBasic(document, this.saasMonitorProblemTypeBarChartData, this.saasMonitorProblemTypeBarChartData[0]["seriesName"], "category", false, false, 'saasMonitorProblemTypeBarChart')
                let saasMonitorProblemTypeBarChart = echarts.getInstanceByDom(document.getElementById("saasMonitorProblemTypeBarChart"))
                saasMonitorProblemTypeBarChart && saasMonitorProblemTypeBarChart.setOption(smallSizeHorizontalBarChartOption)

                // 拿到saasSoftVersionAmount柱状图的数据
                this.saasSoftVersionAmountBarChartData = response.data.data[3]
                updateBarChartBasic(document, this.saasSoftVersionAmountBarChartData, this.saasSoftVersionAmountBarChartData[0]["seriesName"], "category", true, true, 'saasSoftVersionAmountBarChart')
                let saasSoftVersionAmountBarChart = echarts.getInstanceByDom(document.getElementById("saasSoftVersionAmountBarChart"))
                saasSoftVersionAmountBarChart && saasSoftVersionAmountBarChart.setOption(smallSizeBarChartOption)

                // 拿到saasAgencyType饼图的数据function
                this.saasAgencyTypePieChartData = response.data.data[4]
                updatePieChartBasic(document, this.saasAgencyTypePieChartData, this.saasAgencyTypePieChartData[0]["seriesName"], 'saasAgencyTypePieChart')   
                // 额外的饼图设置
                let saasAgencyTypePieChart = echarts.getInstanceByDom(document.getElementById("saasAgencyTypePieChart"))
                saasAgencyTypePieChart && saasAgencyTypePieChart.setOption({
                    series: [{ 
                        radius : ["20%", "37%"], 
                        labelLine: { length: 3, maxSurfaceAngle: 80 },
                        // 给标签设置字体大小
                        label : {
                            rich: {
                                b: {
                                    fontSize: 10,
                                },
                                per: {
                                    fontSize: 10,
                                }
                            }
                        }
                    }]
                })

                // 拿到saasLargeProblemType柱状图的数据
                this.saasLargeProblemTypeBarChartData = response.data.data[5]
                updateBarChartBasic(document, this.saasLargeProblemTypeBarChartData, this.saasLargeProblemTypeBarChartData[0]["seriesName"], "category", false, false, 'saasLargeProblemTypeBarChart')
                let saasLargeProblemTypeBarChart = echarts.getInstanceByDom(document.getElementById("saasLargeProblemTypeBarChart"))
                saasLargeProblemTypeBarChart && saasLargeProblemTypeBarChart.setOption(smallSizeHorizontalBarChartOption)

                // 拿到saasCountrySummaryData表格的的数据
                this.saasCountrySummaryData = response.data.data[6][0]["seriesData"]

            } catch (error) {
                console.log(error)
                this.$message.error('错了哦，仔细看错误信息弹窗')
                alert('失败' + error)
            }
        },

        /**
         * @param {searchValue} searchValue 搜索参数的字典
         * @description 对省份受理数量柱状图的后端数据请求
         */
        async searchSaaSFunctionByProvince(searchValue) {
            try {
                const response = await this.$http.get(
                    '/api/CMC/workrecords/analysis_saas_function_by_province?beginData=' +
                    searchValue['beginData'] +
                    '&endData=' +
                    searchValue['endData'] +
                    '&functionName=' +
                    searchValue['functionName']
                )
                this.saasProvinceBarChartData = response.data.data
                // 将yMax的值取出去除，不让他进入updateBarChartBasic()中，该值用来对省份子集的y轴大小做一个统一，否则y轴会根据里面的数据自适应缩放大小
                this.saasProvinceProblemAmountMax = this.saasProvinceBarChartData.pop().yMax

                updateBarChartBasic(document, this.saasProvinceBarChartData, 'SaaS省份三线受理统计', "category", true, true, 'saasProvinceAndFunctionChart')
                console.log('update local province bar chart data: ', this.saasProvinceBarChartData)
                this.updateSaasProvinceAndFunctionSplitChart()

                // 给图添加一个graphic用于点击使用，进行子集的图的收缩和展开。
                // 在回调函数中this指向的是echart对象，而不是这个document
                var that = this
                let saasProvinceAndFunctionChart = echarts.getInstanceByDom(document.getElementById("saasProvinceAndFunctionChart"))
                saasProvinceAndFunctionChart && saasProvinceAndFunctionChart.setOption({
                    graphic : {
                        type : 'text',
                        left: 'right',
                        top: 'top',
                        z: 100,
                        style : {
                            fill : '#409eff',
                            text : "收缩/展开子集",
                            fontSize: 16,
                            lineHeight: 30,
                            textAlign: 'center',
                            padding : [10, 25, 0, 0],
                        },
                        onclick: function(){
                            for (let i = 0; i < that.provinceSplitNum; i++) {
                                const ele = document.getElementById('saasProvinceAndFunctionChart' + (i + 1));
                                // 根据子集的state进行是否要添加hidden class设置display none
                                (that.provinceSplitState) ? ele.classList.add("hidden") : ele.classList.remove("hidden");
                            }
                            that.provinceSplitState = !that.provinceSplitState                 
                        }
                    }
                })
            } catch (error) {
                console.log(error)
                this.$message.error('错了哦，仔细看错误信息弹窗')
                alert('失败' + error)
            }
        },

        /**
         * @param {searchValue} searchValue 搜索参数的字典
         * @description 对省份受理数量和单位开通数量对比柱状图的后端数据请求
         */
        async searchSaaSProblemByProvinceAgency(searchValue) {
            try {
                const response = await this.$http.get(
                    '/api/CMC/workrecords/analysis_saas_problem_by_province_agency?beginData=' +
                    searchValue['beginData'] +
                    '&endData=' +
                    searchValue['endData']
                )
                this.saasProvinceAndAgencyChartData = response.data.data
                this.updateSaaSProvinceAndAgencyBarChart(this.saasProvinceAndAgencyChartData, 'SaaS全国各省受理统计', "category", true, 'saasProvinceAndAgencyChart')
                console.log('update local province and angency bar chart data: ', this.saasProvinceAndAgencyChartData)

            } catch (error) {
                console.log(error)
                this.$message.error('错了哦，仔细看错误信息弹窗')
                alert('失败' + error)
            }
        },

        /**
         * @param {searchValue} searchValue 搜索参数的字典
         * @description 对省份受理数量和单位开通数量对比柱状图的后端数据请求
         */
        async searchSaaSProblemByMonth(searchValue) {
        try {
            const response = await this.$http.get(
            '/api/CMC/workrecords/analysis_saas_problem_by_month?beginData=' +
            searchValue['beginData'] +
            '&endData=' +
            searchValue['endData']
            )
            this.saasProblemMonthChartData = response.data.data
            updateBarChartBasic(document, this.saasProblemMonthChartData, searchValue['beginData'].slice(0,4)+'年SaaS月份受理统计', "category", false, true, 'saasProblemMonthChart')
            let saasProblemMonthChart = echarts.getInstanceByDom(document.getElementById("saasProblemMonthChart"))
            let functionTypeData = this.saasProblemMonthChartData[0]["seriesData"].map((item) => item.functionType)
            saasProblemMonthChart && saasProblemMonthChart.setOption({
                tooltip: {
                    trigger: 'axis',
                    formatter: function (params) {
                        const index = params[0].dataIndex; // 获取当前数据点的索引
                        const xValue = params[0].name; // x 值
                        const yValue = params[0].value; // y 值
                        // 获取数据点对应的出错功能
                        let func = ''
                        functionTypeData[index].forEach((item)=> { func+= '<br/>' + item.function + ": " + item.amount })
                        return `月份: ${xValue}<br/>受理数量: ${yValue} ${func}`;
                    }
                }
            })
            
            console.log('update local month bar chart data: ', this.saasProblemMonthChartData)

        } catch (error) {
            console.log(error)
            this.$message.error('错了哦，仔细看错误信息弹窗')
            alert('失败' + error)
        }
        },

        /**
         * @param {searchValue} searchValue 搜索参数的字典
         * @description 对版本趋势柱状图的后端数据请求
         */
        async searchSaaSVersionUpgradeTrend(searchValue) {
        try {
            const response = await this.$http.get(
            '/api/CMC/workrecords/analysis_version_upgrade_trend?beginData=' +
            searchValue['beginData'] +
            '&endData=' +
            searchValue['endData'] +
            '&functionName=' +
            searchValue['functionName'] +
            '&provinceSelected=' +
            searchValue['provinceSelected']
            )
            this.saasVersionBarChartData = response.data.data
            updateBarChartBasic(document, this.saasVersionBarChartData, this.provinceSelected+'SaaS全版本受理趋势', "category", false, true, 'saasVersionTrendChart')
            console.log('update local version linechart data: ', this.saasVersionBarChartData)

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

@font-face {
    font-family: "seven_digit_i";
    src: url("../../assets/fonts/digital-7_mono_i.ttf");
}

.saasChinaMapShow {
    display: inline-block;
}

.saasChinaMapShow > div {
    margin-top: 5px;
    border-radius: 8px;
    border: 1px solid skyblue;
}

.threeDText {
  font-size: 16px;
  color: #120CC6;
  text-shadow:0px 1px 0px #c0c0c0,
	 0px 2px 0px #b0b0b0,
	 0px 3px 0px #a0a0a0,
	 0px 4px 0px #909090,
	 0px 5px 10px rgba(0, 0, 0, .9);
}

.sevenDital {
    font-size: 20px;
    color: #1027CA;
    font-family: seven_digit_i;   
}

.normalChartSize {
    width: 100% !important;
    height: 400px !important;
}

.hidden {
    display: none !important;
}

</style>    