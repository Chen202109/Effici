
<template>
    <div>
        <div class="provinceAndFunctionChart normalChartSize" id="provinceAndFunctionChart"></div>
        <div class="provinceAndFunctionChartSplit" id="provinceAndFunctionChartSplit">
            <!-- 因为省份和功能会产生太多柱子，所以对省份进行一个切割，分成多张图来展现，注意，v-for这边生成的i是从1开始，所以id的末尾是1不是0 -->
            <div v-for="i in provinceSplitNum" :class="'provinceAndFunctionChart' + i"
                :id="'provinceAndFunctionChart' + i"></div>
        </div>
    </div>
</template>

<script>
    import { updateBarChartBasic } from '@/utils/echartBasic'
    let echarts = require("echarts/lib/echarts");

    export default {
        name: "provinceAndFunctionChart",
        props: {
            // 省份和出错功能对比的柱形图的数据
            provinceBarChartData: {
                type: Array,
                default() {
                    return ["",""];
                },
            },
            //该值用来对省份子集的y轴大小做一个统一，否则y轴会根据里面的数据自适应缩放大小
            provinceProblemAmountMax : {
                type: Number,
                default() {
                    return 0;
                },
            },
            // 将省份和出错功能对比的柱形图分割成几个子图
            provinceSplitNum : {
                type: Number,
                default() {
                    return 0;
                },
            },
        },
        watch: {
            provinceBarChartData: {
            handler(newVal, oldVal) {
                this.updateProvinceAndFunctionChart()
            }
        }
        },
        data(){
            return {
                // 省份与出错功能柱状图的子集的图的收缩state
                provinceSplitState: false,
            }
        },

        mounted() {
            this.drawCharts();
        },

        methods: {

            // echarts各类图表的init
            drawCharts() {
                echarts.init(document.getElementById('provinceAndFunctionChart'))
            },

            /**
             * 对省份子集的图进行update数据
             */
            updateProvinceAndFunctionSplitChart() {
                let interval = this.provinceBarChartData[0]["seriesData"].length / this.provinceSplitNum
                // 要分成几张图的数据，进行遍历循环，给柱状图添加数据。
                for (let i = 0; i < this.provinceSplitNum; i++) {
                    const ele = document.getElementById('provinceAndFunctionChart' + (i + 1))
                    ele.classList.add('normalChartSize')
                    echarts.init(ele)
                    let splitData = []
                    this.provinceBarChartData.forEach((item) => { splitData.push({ seriesName: item.seriesName, seriesData: item.seriesData.slice(i * interval, (i + 1) * interval) }) })
                    // 将数据注入柱状图内，i+1是因为元素在使用v-for生成的时候，v-for的i是从1开始，这里是0开始，所以使用i+1来获取相同的id
                    updateBarChartBasic(document, splitData, '省份三线受理统计(子集' + (i + 1) + ')', "category", false, true, 'provinceAndFunctionChart' + (i + 1))
                    let chart = echarts.getInstanceByDom(document.getElementById('provinceAndFunctionChart' + (i + 1)))
                    chart && chart.setOption({
                        yAxis: {
                            type: "value",
                            max: Math.ceil(this.provinceProblemAmountMax / 10) * 10
                        }
                    })

                    // 判断是否要隐藏子集
                    if (!this.provinceSplitState && !ele.classList.contains('hidden')) ele.classList.add('hidden')
                }
            },

            /**
             * 对省份与出错功能的图进行update数据
             */
             updateProvinceAndFunctionChart() {
                updateBarChartBasic(document, this.provinceBarChartData, '省份三线受理统计', "category", true, true, 'provinceAndFunctionChart')
                console.log('update local province bar chart data: ', this.provinceBarChartData)
                this.updateProvinceAndFunctionSplitChart()

                // 给图添加一个graphic用于点击使用，进行子集的图的收缩和展开。
                // 在回调函数中this指向的是echart对象，而不是这个document
                var that = this
                let provinceAndFunctionChart = echarts.getInstanceByDom(document.getElementById("provinceAndFunctionChart"))
                provinceAndFunctionChart && provinceAndFunctionChart.setOption({
                    graphic: {
                        type: 'text',
                        left: 'right',
                        top: 'top',
                        z: 100,
                        style: {
                            fill: '#409eff',
                            text: "收缩/展开子集",
                            fontSize: 16,
                            lineHeight: 30,
                            textAlign: 'center',
                            padding: [10, 25, 0, 0],
                        },
                        onclick: function () {
                            for (let i = 0; i < that.provinceSplitNum; i++) {
                                const ele = document.getElementById('provinceAndFunctionChart' + (i + 1));
                                // 根据子集的state进行是否要添加hidden class设置display none
                                (that.provinceSplitState) ? ele.classList.add("hidden") : ele.classList.remove("hidden");
                            }
                            that.provinceSplitState = !that.provinceSplitState
                        }
                    }
                })
            },

        },
    }
</script>

<style scoped>
.normalChartSize {
    width: 100% !important;
    height: 400px !important;
}

.hidden {
    display: none !important;
}
</style>