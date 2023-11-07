<template>
  <div class="upgradeTrend">
    <div style="margin: 15px 0">
      <div>
        <span class="demonstration">资源池： </span>
        <el-select v-model="resourcePoolSelected" multiple placeholder="请选择资源池" style="width: 150px;">
          <el-option v-for="(item, index) in resourcePoolOptions" :key="index" :label="item" :value="item"></el-option>
        </el-select>

        <span class="demonstration" style="margin-left: 15px;">服务名： </span>
        <el-select v-model="serviceSelected" multiple placeholder="请选择服务">
          <el-option v-for="(item, index) in serviceOptions" :key="index" :label="item" :value="item"></el-option>
        </el-select>

        <span class="demonstration" style="margin-left: 15px;">时间范围： </span>
        <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期"
          end-placeholder="结束日期">
        </el-date-picker>
        <el-button type="primary" @click="search">查询</el-button>
      </div>
    </div>

    <div class="saasVersionTrendChart" id="saasVersionTrendChart" :style="{ width: getMainPageWidth, height: '400px' }"></div>

    <div></div>


    <div class="youChart" id="youChart" :style="{ width: '1250px', height: '450px' }"></div>
  </div>
</template>


<script>
// 引入基本模板
let echarts = require("echarts/lib/echarts");
// 引入提示框和title组件
require("echarts/lib/component/tooltip");
require("echarts/lib/component/title");

export default {
  name: 'AnalysisUpgrade_version',
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
      // 资源池选择
      // resourcePoolOptions: ['V3', '01资源池', '02资源池', '03资源池', '04资源池', '运营支撑平台'],
      resourcePoolOptions: ['01资源池', '03资源池', '04资源池'],
      resourcePoolSelected: '',
      // service选择
      serviceOptions: [
        'saas-invoice-ebill-server',
        'saas-billcollection-server',
        'saas-industry-server',
        'saas-finance-adapter-server',
      ],
      serviceSelected: '',
      // 日期查询范围
      dateRange: [
        new Date(
          new Date().getFullYear() + '-' + (new Date().getMonth() + 1) + '-01'
        ),
        new Date(),
      ],

      lineChartData: [],
    }
  },
  // 计算页面刚加载时候渲染的属性
  computed: {
    data() { },
    getMainPageWidth: function(){
      // windows.screen.width返回屏幕宽度，减去侧边栏240px,减去container模型左右padding各20px和margin-right的10px,
      // 减去主页面各自15px的padding, 减去不知道那里vue自己设的30px, 减去主页面内元素和滚动条保持距离的padding-right的10px,
      return (window.screen.width-240-20*2-10-15*2-30-10)+'px'
    },
  },
  // 在初始化页面完成后,再对dom节点上图形进行相关绘制
  mounted() {
    console.log('升级汇报-分析升级', this.versionData);
    this.drawLine();
  },

  methods: {
    drawLine() {
      // 基于准备好的dom，初始化echarts实例
      let youChart = echarts.init(document.getElementById('youChart'))

      var option;
      const data = [["v1.13.0", 116], ["v1.13.1", 129], ["2000-06-07", 135], ["2000-06-08", 86], ["2000-06-09", 73], ["v1.13.1", 85], ["2000-06-11", 73], ["2000-06-12", 68], ["v1.13.4", 92], ["2000-06-14", 130], ["v1.13.3", 245], ["2000-06-16", 139], ["2000-06-17", 115], ["2000-06-18", 111], ["2000-06-19", 309], ["v1.13.4", 206], ["v1.13.6", 137], ["2000-06-22", 128], ["2000-06-23", 85], ["2000-06-24", 94], ["v1.13.7", 71], ["2000-06-26", 106], ["2000-06-27", 84], ["2000-06-28", 93], ["v1.14.0", 85], ["v1.14.1", 73], ["2000-07-01", 83], ["2000-07-02", 125], ["2000-07-03", 107], ["2000-07-04", 82], ["v1.14.2", 44], ["2000-07-06", 72], ["v1.14.3", 106], ["2000-07-08", 107], ["2000-07-09", 66], ["v1.14.4", 91], ["2000-07-11", 92], ["2000-07-12", 113], ["2000-07-13", 107], ["2000-07-14", 131], ["v1.14.5", 111], ["2000-07-16", 64], ["2000-07-17", 69], ["2000-07-18", 88], ["2000-07-19", 77], ["2000-07-20", 83], ["2000-07-21", 111], ["2000-07-22", 57], ["v1.14.6", 55], ["2000-07-24", 60]];
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


      // saas version和bug的折线图绘制
      let saasVersionTrendChart = echarts.init(document.getElementById('saasVersionTrendChart'))
      option = {
        title : {
          top: '1%',
          text: 'SaaS版本三线受理趋势',
          left: 'center'
        },
        legend: {
          top: '7%',
          data: []
        },
        grid: {
          top: '30%',
          bottom: '30%',
          left: '5%',
          right: '5%',
        },
        xAxis: {
          type: 'time'
        },
        yAxis: {
          type: 'value'
        },
        
        series: []
      };
      saasVersionTrendChart.setOption(option);

    },

    updateSaaSTrendLineChart(){
      let versionData = []
      let currentVersion = []
      let series = []
      let legendData = []
      for (let i = 0; i < this.lineChartData.length; i++) {
        versionData.push(this.lineChartData[i].data.map((item) => item.version))
        currentVersion.push('')
        let data1 = this.lineChartData[i].data
        let series_1 = {
          name: this.lineChartData[i].service,
          type: 'line',
          data: this.lineChartData[i].data.map((item) => [item.x, item.y]),
          label: {
            show: true,
            formatter: function (params) {
              const index = params.dataIndex; // 当前数据点的索引
              const version = data1[index].version; // 获取当前数据点的版本号
              if (version !== currentVersion[i]) {
                // 如果版本号变动
                currentVersion[i] = version; // 更新当前版本号
                return version; // 显示版本号
              }
              return ''; // 如果版本号未变动，则不显示 label
            },
            position: 'top'
          }
        };
        series.push(series_1)
        legendData.push(this.lineChartData[i].service)
      }


      let tooltip = {
        trigger: 'axis',
        formatter: function (params) {
          const index = params[0].dataIndex; // 获取当前数据点的索引
          const xValue = params[0].value[0]; // x 值
          const yValue = params[0].value[1]; // y 值
          const version = versionData[params[0].seriesIndex][index]; // 获取对应版本号
          return `X: ${xValue}<br/>Y: ${yValue}<br/>Version: ${version}`;
        }
      };

      console.log('updated local series: ', series)
      
      let saasVersionTrendChart = echarts.getInstanceByDom(document.getElementById('saasVersionTrendChart'))
      if (saasVersionTrendChart){
        saasVersionTrendChart.setOption({
          tooltip: tooltip,
          series : series,
          legend: {
            data: legendData
          }
        })
      } 

      console.log("updated echart linechart: ", saasVersionTrendChart)

    },


    async search() {
      // 触发查询事件，根据日期条件进行查询
      var searchValue = {} // 存放筛选条件信息
      searchValue['resourcePool'] = this.resourcePoolSelected.toString()
      searchValue['serviceName']  = this.serviceSelected.toString()
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

      try {
        const response = await this.$http.get(
          '/api/CMC/workrecords/analysis_service_upgrade_trend?beginData=' +
          searchValue['beginData'] +
          '&endData=' +
          searchValue['endData'] +
          '&resourcePool=' +
          searchValue['resourcePool'] +
          '&serviceName=' +
          searchValue['serviceName'] 
        )
        this.lineChartData = response.data.data
        this.updateSaaSTrendLineChart()
        console.log('update local linechart data: ', this.lineChartData)
        
      } catch (error) {
        console.log(error)
        this.$message.error('错了哦，仔细看错误信息弹窗')
        alert('失败' + error)
      }
    },
  }
}
</script>


<style>
.el-dropdown-link {
  cursor: pointer;
  color: #409EFF;
}

.el-icon-arrow-down {
  font-size: 12px;
}
</style>