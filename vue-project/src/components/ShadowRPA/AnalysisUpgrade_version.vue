<template>
  <div class="Upgrade_version">
    <div class="youChart" id="youChart" :style="{ width: '750px', height: '450px' }"></div>
  </div>
</template>


<script>
// 引入基本模板
let echarts = require("echarts/lib/echarts");
// 引入柱状图组件
require("echarts/lib/chart/bar");
// 引入提示框和title组件
require("echarts/lib/component/tooltip");
require("echarts/lib/component/title");

export default {
    name : 'AnalysisUpgrade_version',
    props: {
      versionData: {
        type: Array,
        default() {
          return [];
        },
      },
    },
    data() {
      return {
        // tableData: [{
        //   date: '2016-05-03',
        //   name: '王小虎',
        //   address: '上海市普陀区金沙江路 1518 弄'
        // }]
      }
    },
      // 在初始化页面完成后,再对dom节点上图形进行相关绘制
    mounted() {
        console.log('升级汇报-分析升级',this.versionData);
        this.drawLine();
    },
    methods: {
      drawLine() {
      // 基于准备好的dom，初始化echarts实例
      let youChart = echarts.init(document.getElementById('youChart'))
    //   // 绘制图表
    //   youChart.setOption({
    //     title: { text: 'ECharts 入门示例' },
    //     tooltip: {//设置鼠标悬停提示框的位置。
    //     //   trigger: 'axis',
    //     //   position: [20, 20]
    //     //   // 等价于
    //     //   // position: ['20px', '20px']
    //     },
    //     xAxis: {
    //       data: ["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"]
    //     },
    //     yAxis: {},
    //     series: [{
    //       name: '销量',
    //       type: 'bar',
    //       data: [5, 20, 36, 10, 10, 20]
    //     }]
    //   });  
    // prettier-ignore
var option;
const data = [["v1.13.0", 116], ["2000-06-06", 129], ["2000-06-07", 135], ["2000-06-08", 86], ["2000-06-09", 73], ["2000-06-10", 85], ["2000-06-11", 73], ["2000-06-12", 68], ["v1.13.4", 92], ["2000-06-14", 130], ["2000-06-15", 245], ["2000-06-16", 139], ["2000-06-17", 115], ["2000-06-18", 111], ["2000-06-19", 309], ["2000-06-20", 206], ["v1.13.6", 137], ["2000-06-22", 128], ["2000-06-23", 85], ["2000-06-24", 94], ["2000-06-25", 71], ["2000-06-26", 106], ["2000-06-27", 84], ["2000-06-28", 93], ["v1.14.0", 85], ["2000-06-30", 73], ["2000-07-01", 83], ["2000-07-02", 125], ["2000-07-03", 107], ["2000-07-04", 82], ["2000-07-05", 44], ["2000-07-06", 72], ["v1.14.3", 106], ["2000-07-08", 107], ["2000-07-09", 66], ["2000-07-10", 91], ["2000-07-11", 92], ["2000-07-12", 113], ["2000-07-13", 107], ["2000-07-14", 131], ["v1.14.5", 111], ["2000-07-16", 64], ["2000-07-17", 69], ["2000-07-18", 88], ["2000-07-19", 77], ["2000-07-20", 83], ["2000-07-21", 111], ["2000-07-22", 57], ["v1.14.6", 55], ["2000-07-24", 60]];
const dateList = data.map(function (item) {
  return item[0];
});
const valueList = data.map(function (item) {
  return item[1];
});
option = {
  // Make gradient line here
  visualMap: [
    {
      show: false,
      type: 'continuous',
      seriesIndex: 0,
      min: 0,
      max: 400
    },
    {
      show: false,
      type: 'continuous',
      seriesIndex: 1,
      dimension: 0,
      min: 0,
      max: dateList.length - 1
    }
  ],
  title: [
    {
      left: 'left',
      text: '        开票功能saas-industry-server三线受理趋势'
    },
    {
      top: '46%',
      left: 'left',
      text: '        数据同步saas-finance-adapter-server三线受理趋势'
    }
  ],
  tooltip: {
    trigger: 'axis'
  },
  xAxis: [
    {
      data: dateList
    },
    {
      data: dateList,
      gridIndex: 1
    }
  ],
  yAxis: [
    {},
    {
      gridIndex: 1
    }
  ],
  grid: [
    {
      bottom: '60%'
    },
    {
      top: '60%'
    }
  ],
  series: [
    {
      type: 'line',
      showSymbol: true,
      data: valueList,
      markPoint: {
        data: [
        { type: 'max', name: '最大值' },
        { type: 'min', name: '最小值' }
        ],
        label: {
        show: true,
        formatter: '{c}'
        }
      }
    },
    
    {
      type: 'line',
      showSymbol: true,
      data: valueList,
      xAxisIndex: 1,
      yAxisIndex: 1,
      markLine: {
        data: [
        { type: 'max', name: '最大值' },
        { type: 'min', name: '最小值' }
        ],
        label: {
        show: true,
        formatter: '{c}'
        }
      }
    }
  ]
};

option && youChart.setOption(option); 
    }
   }
}
</script>


<style>
<style>