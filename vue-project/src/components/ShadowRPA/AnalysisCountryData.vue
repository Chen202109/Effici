<template>
    <div>
        <div style="margin: 15px 0">
            <div>
                <span class="demonstration">时间范围： </span>
                <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期"
                    end-placeholder="结束日期">
                </el-date-picker>
                <el-button type="primary" @click="search">查询</el-button>
            </div>
            <!-- 功能分类 -->
            <div>
                <div style="margin-bottom: 10px;">
                    <span class="demonstration">业务分类： </span>
                    <el-checkbox-group v-model="businessSelected" @change="businessCheckBoxChange" style="display: inline-block;">
                    <el-checkbox v-for="(item, index) in businessOptions" :key="index" :label="item">{{ item }}</el-checkbox>
                    </el-checkbox-group>
                </div>

                <div>
                    <span class="demonstration">功能分类： </span>
                    <el-checkbox-group v-model="functionSelected" style="display: inline-block;">
                    <el-checkbox v-for="(item, index) in functionOptions[this.businessSelected]" :key="index" :label="item">{{
                        item }}</el-checkbox>
                    </el-checkbox-group>
                </div>
            </div>
        </div>
        <!-- 容器 -->
        <div id="saasProblemChinaMap" ref="saasProblemChinaMap"
            :style="{ width: getMainPageWidth * 0.6 + 'px', height: '600px', margin: 'auto' }"></div>
        <div class="saasProvinceAndFunctionChart" id="saasProvinceAndFunctionChart"
            :style="{ width: getMainPageWidth + 'px', height: '400px' }"></div>
        <div class="saasProvinceAndFunctionChartSplit" id="saasProvinceAndFunctionChartSplit">
            <!-- 因为省份和功能会产生太多柱子，所以对省份进行一个切割，分成多张图来展现，注意，v-for这边生成的i是从1开始，所以id的末尾是1不是0 -->
            <div v-for="i in provinceSplitNum" :class="'saasProvinceAndFunctionChart' + i"
                :id="'saasProvinceAndFunctionChart' + i" :style="{ width: getMainPageWidth + 'px', height: '400px' }">
            </div>
        </div>
        <div class="saasProvinceAndAgencyChart" id="saasProvinceAndAgencyChart"
            :style="{ width: getMainPageWidth + 'px', height: '400px' }"></div>
    </div>
</template>
  
<script>
import { updateBarChartBasic } from '@/utils/echartBasic'

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
            chinaMapProvinceSaaSProblemData: [{ "seriesName": "全国省份受理数据", "seriesData": 1 }],
            // 业务选择
            businessOptions: ['日常业务', '其他业务'],
            businessSelected: [],
            // 功能选择
            functionOptions: {
                "日常业务": ["开票功能", "收缴业务", "核销功能", "打印功能", "报表功能", "票据管理", "通知交互", "反算功能", "数据同步"],
                "其他业务": ["增值服务", "单位开通", "license重置", "安全漏洞"],
            },
            functionSelected: '',

            // 将省份和出错功能对比的柱形图分割成几个子图
            provinceSplitNum : 2,
            
            saasProvinceBarChartData: [],
            saasProvinceAndAgencyChartData: [],
        }
    },
    // 计算页面刚加载时候渲染的属性
    computed: {
        /**
         * 获取主页面宽度的60%，用于给地图的布局的设置
         */
         getMainPageWidth: function () {
            // windows.screen.width返回屏幕宽度，减去侧边栏240px,减去container模型左右padding各20px和margin-right的10px,
            // 减去主页面各自15px的padding, 减去不知道那里vue自己设的30px, 减去主页面内元素和滚动条保持距离的padding-right的10px,
            return (window.screen.width - 240 - 20 * 2 - 10 - 15 * 2 - 30 - 10)
        },
    },
    mounted() {
        this.businessSelected.push(this.businessOptions[0]);
        this.functionSelected = this.functionOptions[this.businessSelected].slice(0, 3);
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

        drawCharts() {
            // 在 mounted 钩子中初始化 china map echarts 实例，并获取容器
            this.saasProblemChinaMap = echarts.init(document.getElementById('saasProblemChinaMap'))
            // ECharts 配置项
            const option = {
                tooltip: {
                    triggerOn: 'mousemove',
                    formatter: function (e) {
                        return e.name + '：' + e.value
                    }
                },
                // geo为地理坐标系组件，用于地图的绘制，支持在地理坐标系上绘制散点图，线集。
                geo: {
                    map: 'china', // 使用 registerMap 注册的地图名称。
                    zoom: 1.1,
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

            // 其他图表的init
            echarts.init(document.getElementById('saasProvinceAndFunctionChart'))
            echarts.init(document.getElementById('saasProvinceAndAgencyChart'))
            // 因为是使用v-for生成的元素，所以使用this.$nextTick来进行延迟，否则可能会出现还没渲染元素就init的情况
            this.$nextTick(() => { for (let i = 0; i < this.provinceSplitNum; i++) echarts.init(document.getElementById('saasProvinceAndFunctionChart' + (i + 1))) })

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

        async search() {
            var searchValue = {} // 存放筛选条件信息
            searchValue['function_name'] = this.functionSelected.toString()
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
            
            this.searchSaaSCountryData(searchValue)
            this.searchSaaSFunctionByProvince(searchValue)
            this.searchSaaSProblemByProvinceAgency(searchValue)
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
                    '&function_name=' +
                    searchValue['function_name']
                )
                this.saasProvinceBarChartData = response.data.data
                // 将yMax的值取出去除，不让他进入updateBarChartBasic()中，该值用来对省份子集的y轴大小做一个统一，否则y轴会根据里面的数据自适应缩放大小
                let yMax = this.saasProvinceBarChartData.pop().yMax

                updateBarChartBasic(document, this.saasProvinceBarChartData, 'SaaS省份三线受理统计', "category", true, 'saasProvinceAndFunctionChart')
                console.log('update local province bar chart data: ', this.saasProvinceBarChartData)

                let interval = this.saasProvinceBarChartData[0]["seriesData"].length / this.provinceSplitNum
                // 要分成几张图的数据，进行遍历循环，给柱状图添加数据。
                for (let i = 0; i < this.provinceSplitNum; i++) {
                    let splitData = []
                    this.saasProvinceBarChartData.forEach((item) => { splitData.push({ seriesName: item.seriesName, seriesData: item.seriesData.slice(i * interval, (i + 1) * interval) }) })
                    // 将数据注入柱状图内，i+1是因为元素在使用v-for生成的时候，v-for的i是从1开始，这里是0开始，所以使用i+1来获取相同的id
                    updateBarChartBasic(document, splitData, 'SaaS省份三线受理统计(子集' + (i + 1) + ')', "category", false, 'saasProvinceAndFunctionChart' + (i + 1))
                    let chart = echarts.getInstanceByDom(document.getElementById('saasProvinceAndFunctionChart' + (i + 1)))
                    chart.setOption({
                        yAxis: {
                            type: "value",
                            max: Math.ceil(yMax / 10) * 10
                        }
                    })
                }

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
    },
};
</script>