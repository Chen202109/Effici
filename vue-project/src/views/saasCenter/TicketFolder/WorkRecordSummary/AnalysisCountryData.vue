
<template>
    <div>
        <div style="margin: 15px 0">
            <template>
                <div class="block">
                <span class="demonstration">分析范围： </span>
                <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期"
                    end-placeholder="结束日期">
                </el-date-picker>
                <el-button type="primary" @click="search">查询</el-button>
                </div>
            </template>

            <div style="height: 10px;"></div>

            <div>
                <span class="demonstration">功能分类： </span>
                <el-checkbox-group v-model="functionSelected" style="display: inline-block;">
                    <el-checkbox v-for="(item, index) in functionOptions" :key="index" :label="item">{{ item }}</el-checkbox>
                </el-checkbox-group>
            </div>
        </div>

        <provinceAndFunctionChart 
            :provinceBarChartData="this.ticketFolderProvinceBarChartData"
            :provinceProblemAmountMax = "this.ticketFolderProvinceProblemAmountMax"
            :provinceSplitNum = "this.provinceSplitNum">
        </provinceAndFunctionChart>
    </div>
</template>

<script>
import { getMainPageWidth } from '@/utils/layoutUtil'
import provinceAndFunctionChart from '@/components/ShadowRPA/AnalysisData/AnalysisProvinceFunctionChart.vue'
let echarts = require("echarts/lib/echarts");

    export default {
        components: {
            provinceAndFunctionChart
        },
        data(){
            return {
                //查询日期
                dateRange: [new Date(new Date().getFullYear() + '-01-01'), new Date()],

                // 票夹的出错功能
                functionOptions: ["单位注册开通", "票夹渠道配置", "单位票据交付","票夹交付归集", "H5挂件展示", "票夹预览票据", "微信卡包插卡", "用户注册登录"],
                functionSelected: [],

                // 将省份和出错功能对比的柱形图分割成几个子图
                provinceSplitNum: 2,
                // 省份与出错功能柱状图的子集的图的收缩state
                provinceSplitState: false,

                ticketFolderProvinceBarChartData: [],
                ticketFolderProvinceProblemAmountMax: 0, //该值用来对省份子集的y轴大小做一个统一，否则y轴会根据里面的数据自适应缩放大小
            }
        },

        // 计算页面刚加载时候渲染的属性
        computed: {
            getPageWidth: getMainPageWidth
        },

        mounted() {
            this.drawCharts();
        },

        methods: {

            // echarts各类图表的init
            drawCharts() {
                echarts.init(document.getElementById('ticketFolderProvinceAndFunctionChart'))
            },

            /**
             * 点击查询按钮之后搜索各个图的后端数据
             */
            async search() {
                var searchValue = {}
                // 获取年、月、日，进行拼接
                for (let i = 0; i < this.dateRange.length; i++) {
                    var year = this.dateRange[i].getFullYear()
                    var month = ('0' + (this.dateRange[i].getMonth() + 1)).slice(-2)
                    var day = ('0' + this.dateRange[i].getDate()).slice(-2)
                    searchValue[i == 0 ? 'beginData' : 'endData'] = year + '-' + month + '-' + day;
                }
                searchValue['functionName'] = this.functionSelected.toString()
                this.searchTicketFolderFunctionByProvince(searchValue)
            },

            /**
             * @param {searchValue} searchValue 搜索参数的字典
             * @description 对省份受理数量柱状图的后端数据请求
             */
            async searchTicketFolderFunctionByProvince(searchValue) {
                this.$http.get(
                    '/api/CMC/workrecords/analysis_ticket_folder_function_by_province?beginData=' +
                    searchValue['beginData'] +
                    '&endData=' +
                    searchValue['endData'] +
                    '&functionName=' +
                    searchValue['functionName']
                ).then(response => {
                    this.ticketFolderProvinceBarChartData = response.data.data
                    // 将yMax的值取出去除，不让他进入updateBarChartBasic()中，该值用来对省份子集的y轴大小做一个统一，否则y轴会根据里面的数据自适应缩放大小
                    this.ticketFolderProvinceProblemAmountMax = response.data.yMax
                }).catch((error) => {
                    console.log(error)
                    console.log(error.response.data.message)
                    this.$message.error(error.response.data.message)
                })
            },
        },
    }
</script>