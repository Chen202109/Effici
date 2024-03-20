<template>
    <div class="analyasisRobot">
        <div style="margin: 15px 0">
            <span class="demonstration" style="margin-left: 15px;">时间范围： </span>
            <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期"
                end-placeholder="结束日期">
            </el-date-picker>
            <el-button type="primary" @click="search">查询</el-button>
        </div>

        <!-- 首页汇总数据 -->
        <div>
            <div class="dashBoardFlexBox" :style="{ width: getPageWidth + 'px', height: '300px' }">
                <el-col v-for="(row, rowIndex) in robotSummaryDashBoardData" :key="rowIndex" class="dashBoardFlexBoxItem">
                    <el-row style="font-size: 16px; margin-bottom: 10px;">{{ row.x }}</el-row>
                    <el-row style="font-size: 28px; font-weight: 550; margin-bottom: 10px;">{{ row.y }}</el-row>
                </el-col>
            </div>
        </div>

        <!-- 汇总数据折线图 -->
        <div>
            <div class="robotAnswerAmountSummaryLineChart" id="robotAnswerAmountSummaryLineChart"
                :style="{ width: getPageWidth + 'px', height: '400px' }">
            </div>
            <div class="robotAnswerIndicatorSummaryLineChart" id="robotAnswerIndicatorSummaryLineChart"
                :style="{ width: getPageWidth + 'px', height: '400px' }">
            </div>
        </div>
    </div>
</template>


<script>
import { getMainPageWidth } from '@/utils/layoutUtil'
import { updateLineChartBasic } from '@/utils/echartBasic'
import { castFloatToPercent } from '@/utils/typeCast'
let echarts = require("echarts/lib/echarts");

export default {
    name: 'AnalysisTicketFolderCustomerServiceRobot',
    data() {
        return {
            // 日期查询范围
            dateRange: [new Date(new Date().getFullYear() + '-' + (new Date().getMonth() + 1) + '-01'), new Date()],

            // 图表数据
            robotSummaryDashBoardData: [],
            robotSummaryLineChartData: [],
        }
    },

    // 计算页面刚加载时候渲染的属性
    computed: {
        data() { },
        getPageWidth: getMainPageWidth
    },

    // 在初始化页面时对dom节点上图形进行基础属性的渲染
    mounted() {
        // 对图标进行一个初始化
        this.drawLine();
    },

    methods: {

        /**
         * 用于使用echarts进行图标的基础绘制init
         */
        drawLine() {
            // 客服机器人数据汇总折线图的init
            echarts.init(document.getElementById('robotAnswerAmountSummaryLineChart'))
            echarts.init(document.getElementById('robotAnswerIndicatorSummaryLineChart'))
        },

        /**
         * 按下查询按钮之后异步查询更新页面图标数据。
         */
        async search() {
            // 触发查询事件，根据日期条件进行查询
            var searchValue = {} // 存放筛选条件信息
            // 获取年、月、日，进行拼接
            for (let i = 0; i <this.dateRange.length; i++) {
                var year = this.dateRange[i].getFullYear()
                var month = ('0' + (this.dateRange[i].getMonth() + 1)).slice(-2)
                var day = ('0' + this.dateRange[i].getDate()).slice(-2)
                searchValue[(i == 0) ? "beginData" : "endData"] = year + "-" + month + "-" + day;
            } //结束for，完成日期的拼接

            this.searchTicketFolderCustomerServiceRobotSummary(searchValue)
        },

        /**
         * @param {Object} searchValue 搜索参数的字典
         * @description 对票夹机器人汇总数据的后端数据请求
         */
        async searchTicketFolderCustomerServiceRobotSummary(searchValue) {
            this.$http.get(
                '/api/CMC/workrecords/ticket_folder/analysis_customer_service_robot_summary?beginData=' +
                searchValue['beginData'] +
                '&endData=' +
                searchValue['endData']
            ).then(response => {
                this.robotSummaryLineChartData = response.data.data

                // 将summary的数据获取到，并根据汇总种类拆分开
                // precision1是因为数据库查的时候precision是关键字，所以使用precision1替代，之后也可在后端进行额外处理
                let sessionAmountData = []; let sessionAmountTotal=0;
                let msgAmountData = []; let msgAmountTotal=0;
                let precisionData = []; let precisionTotal=0;
                let recallData = []; let recallTotal=0;
                this.robotSummaryLineChartData.map((item) => {
                    sessionAmountData.push({ "x": item.date, "y": item.sessionAmount })
                    sessionAmountTotal += item.sessionAmount
                    msgAmountData.push({ "x": item.date, "y": item.msgAmount })
                    msgAmountTotal += item.msgAmount
                    precisionData.push({ "x": item.date, "y": item.precision1 })
                    precisionTotal += item.precision1
                    recallData.push({ "x": item.date, "y": item.recall })
                    recallTotal += item.recall
                })

                // 更新dashBoard的展示数据
                this.robotSummaryDashBoardData = [
                    { "x": "消息量(合计)", "y": msgAmountTotal },
                    { "x": "会话量(合计)", "y": sessionAmountTotal },
                    { "x": "精确率(平均)", "y": castFloatToPercent(precisionTotal/this.robotSummaryLineChartData.length) },
                    { "x": "召回率(平均)", "y": castFloatToPercent(recallTotal/this.robotSummaryLineChartData.length) },
                ]

                // 将数据封在两个折线图表数据内
                let amountData = []
                amountData.push({ "seriesName": "会话量", "seriesData": sessionAmountData })
                amountData.push({ "seriesName": "消息量", "seriesData": msgAmountData })
                let indicatorData = []
                indicatorData.push({ "seriesName": "准确率", "seriesData": precisionData })
                indicatorData.push({ "seriesName": "召回率", "seriesData": recallData })

                // 更新两个汇总数据的折线图
                updateLineChartBasic(document, amountData, "票夹客服数据汇总(消息数/会话数)", "robotAnswerAmountSummaryLineChart")
                updateLineChartBasic(document, indicatorData, "票夹客服数据汇总(精确度/召回率)", "robotAnswerIndicatorSummaryLineChart")

            }).catch((error) => {
                console.log(error)
                console.log(error.response.data.message)
                this.$message.error(error.response.data.message)
            })
        },

    },
}
</script>

<style scoped>
.saasAnalysisTitle {
    color: #3398DB;
    font-size: 18px;
    margin: 5px 10px 5px 0;
}


.dashBoardFlexBox{
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
}

/* width 就是计算宽度，但是因为有border的存在，所以不能直接除以列数，需要留有1%或者2%的空余 */
/* line-height 是为了让竖直居中，计算方法为外部div的height/(col的数量/2) * 2 */
.dashBoardFlexBoxItem{
    width: 49%; 
    text-align: center; 
    background-color: #f6f8f9;
    /* border: #fff 3px solid; */
    border-radius: 8px;
    margin-bottom: 20px;
    box-sizing: border-box;
    padding: 20px 0;
}
</style>