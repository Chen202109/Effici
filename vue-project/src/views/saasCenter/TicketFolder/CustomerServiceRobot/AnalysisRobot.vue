<template>
    <div class="analyasisRobot">
        <div style="margin: 15px 0">
            <span class="demonstration" style="margin-left: 15px;">时间范围： </span>
            <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期"
                end-placeholder="结束日期">
            </el-date-picker>
            <el-button type="primary" @click="search">查询</el-button>
        </div>


        
        <div>
            <p class="saasAnalysisTitle"> 票夹客服数据汇总</p>
            <el-radio-group v-model="summaryTypeSelected">
                <el-radio-button v-for="(item, index) in summaryTypeOptions" :key="index" :label="item"></el-radio-button>
            </el-radio-group>

            <div class="robotSummaryLineChart" id="robotSummaryLineChart" :style="{ width: getPageWidth + 'px', height: '400px' }">
            </div>
        </div>
    </div>
</template>


<script>
import { getMainPageWidth } from '@/utils/layoutUtil'
    export default {
      name : 'AnalysisTicketFolderCustomerServiceRobot',
      data() {
        return {
            // 日期查询范围
            dateRange: [new Date(new Date().getFullYear() + '-' + (new Date().getMonth() + 1) + '-01'),new Date()],

            // 汇总类型
            summaryTypeOptions: ['消息量', '会话量', '召回率', "精确率"],
            summaryTypeSelected: '',

            // 图表数据
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
            this.summaryTypeSelected = this.summaryTypeOptions[0];
            // 对图标进行一个初始化
            this.drawLine();
        },
  
      methods: {

        /**
         * 用于使用echarts进行图标的基础绘制init
         */
        drawLine() {
            // 客服机器人数据汇总折线图的init
            echarts.init(document.getElementById('robotSummaryLineChart'))
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
            searchValue["summaryType"] = this.summaryTypeSelected

            this.searchTicketFolderCustomerRobotSummary(searchValue)
        },

        /**
         * @param {Object} searchValue 搜索参数的字典
         * @description 对票夹机器人汇总数据的后端数据请求
         */
        async searchTicketFolderCustomerRobotSummary(searchValue) {
        this.$http.get(
                '/api/CMC/workrecords/analysis_saas_service_upgrade_trend?beginData=' +
                searchValue['beginData'] +
                '&endData=' +
                searchValue['endData'] +
                '&resourcePool=' +
                searchValue['resourcePool'] 
            ).then(response => {
                this.robotSummaryLineChartData = response.data.data
                this.updateLineChart(this.robotSummaryLineChartData,"","")
                console.log('update local linechart data: ', this.saasUpgradeLineChartData)
            }).catch((error) => {
                console.log(error)
                console.log(error.response.data.message)
                this.$message.error(error.response.data.message)
            })
        },

        /**
         * @param {Object} chartData 需要传入的图表数据
         * @param {Object} chartTitle 图表标题
         * @param {Object} chartElementId 图表元素id
         * @description 当查询之后，数据更新，更新饼状图。
         */
        updateLineChart(chartData, chartTitle,chartElementId){
            // 对option的基础设置
            let option = {
                title: {
                    top: '1%',
                    left: '5%',
                    text: chartTitle,
                    left: 'left'
                },
                legend: {
                    top: '8%',
                    data: []
                },
                grid: {
                    top: '23%',
                    bottom: '20%',
                    left: '5%',
                    right: '5%',
                },
                xAxis: {
                    name: '时间',
                    nameLocation: 'middle',
                    nameGap: 25,
                    nameTextStyle: {
                        fontSize: 16,
                    },
                    type: 'time',
                    data : [],
                },
                yAxis: {
                    name: '数量',
                    nameLocation: 'middle',
                    nameGap: 25,
                    nameTextStyle: {
                        fontSize: 16,
                    },
                    type: 'value',
                },
                series: [],
            };

            // 设置series

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
    
  </style>