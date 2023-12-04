<template>
  <div class="upgradeTrend">
    <div style="margin: 15px 0">
      <div>
        <div style="margin-bottom: 10px;">

          <span class="demonstration">资源池： </span>
          <el-radio-group v-model="resourcePoolSelected">
            <el-radio-button v-for="(item, index) in resourcePoolOptions" :key="index" :label="item"></el-radio-button>
          </el-radio-group>

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
    </div>

    <div class="saasUpgradeTrendChart" id="saasUpgradeTrendChart" :style="{ width: getMainPageWidth+ 'px', height: '400px' }">
    </div>
    <div class="saasVersionTrendByResourcePoolChart" id="saasVersionTrendByResourcePoolChart" :style="{ width: getMainPageWidth+ 'px', height: '400px' }">
    </div>
    <div class="saasVersionTrendChart" id="saasVersionTrendChart" :style="{ width: getMainPageWidth+ 'px', height: '400px' }">
    </div>
    <div class="saasProblemMonthChart" id="saasProblemMonthChart" :style="{ width: getMainPageWidth+ 'px', height: '400px' }">
    </div>
    <div>
      <div class="saasLargeProblemTypeChart" id="saasLargeProblemTypeChart" :style="{ width: getMainPageWidth * 0.65+ 'px', height: '600px' }">
      </div>
      <div class="saasLargeProblemTopTable" style="width: 35%;">
        <p>私有化重大故障问题总计受理: <span style="color: red;">{{ saasLargeProblemTypeChartData[2]['seriesData'] }}</span> 次</p>
        <el-table
          :data="saasLargeProblemTypeChartData[1]['seriesData']" 
          :header-cell-style="{fontSize:'14px',background: 'rgb(64 158 255 / 65%)',color:'#696969',}"
          :cell-style="{fontSize: 12 + 'px',}"
           style="width: 100%; margin: auto">
          <el-table-column label="私有化重大故障Top10分类" align="center">
            <el-table-column
              v-for="(item, index) in saasLargeProblemTopTableTitle" :key="index" :prop="item.prop" :label="item.label"
              :width="columnWidth(item.label, 'saasLargeProblemTopTable')"  align="center">
            </el-table-column>
          </el-table-column>  
        </el-table>
      </div>
    </div>

    <div></div>

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
  name: 'AnalysisUpgradeTrend',
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
      resourcePoolOptions: ['01资源池', '03资源池', '04资源池'],
      resourcePoolSelected: '',
      // 业务选择
      businessOptions: ['日常业务', '其他业务'],
      businessSelected: [],
      // 功能选择
      functionOptions: {
        "日常业务": ["开票功能", "收缴业务", "核销功能", "打印功能", "报表功能", "票据管理", "通知交互", "反算功能", "数据同步"],
        "其他业务": ["增值服务", "单位开通", "license重置", "安全漏洞"],
      },
      functionSelected: '',
      // 日期查询范围
      dateRange: [new Date(new Date().getFullYear() + '-01-01'), new Date()],
      // 重大故障的表的数据
      saasLargeProblemTopTableTitle: [
        {'prop': "name", "label": "问题分类"},
        {'prop': "value", "label": "次数"},
        {'prop': "percent", "label": "百分比"}
      ],

      // 这个页面各类图的数据
      saasUpgradeLineChartData: [],
      saasVersionByResoucePoolBarChartData: [],
      saasVersionBarChartData: [],
      saasProvinceBarChartData: [],
      saasProvinceAndAgencyChartData: [],
      saasProblemMonthChartData: [],
      saasLargeProblemTypeChartData: [ 
        {'seriesName': "私有化重大故障数量", 'seriesData': []}, 
        {'seriesName': "私有化重大故障top10", 'seriesData': []}, 
        {'seriesName': "私有化重大故障数量合计", 'seriesData': 0}
      ],
    }
  },
  // 计算页面刚加载时候渲染的属性
  computed: {
    data() { },
    getMainPageWidth: function () {
      // windows.screen.width返回屏幕宽度，减去侧边栏240px,减去container模型左右padding各20px和margin-right的10px,
      // 减去主页面各自15px的padding, 减去不知道那里vue自己设的30px, 减去主页面内元素和滚动条保持距离的padding-right的10px,
      return (window.screen.width - 240 - 20 * 2 - 10 - 15 * 2 - 30 - 10) 
    },
  },
  // 在初始化页面完成后,再对dom节点上图形进行相关绘制
  mounted() {
    console.log('升级汇报-分析升级', this.versionData);
    // 页面初始化后对checkbox,下拉列表组件添加初始值
    this.resourcePoolSelected = this.resourcePoolOptions[0];
    this.businessSelected.push(this.businessOptions[0]);
    this.functionSelected = this.functionOptions[this.businessSelected].slice(0, 3);
    // 对图标进行一个初始化
    this.drawLine();
  },

  methods: {
    //业务类型的checkbox单选功能
    businessCheckBoxChange(value) {
      if (this.businessSelected.length > 1) {
        this.businessSelected.splice(0, 1)
      }
      this.functionSelected = this.functionOptions[this.businessSelected];
    },

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
      if (tableName === 'saasLargeProblemTopTable' && key === '问题分类') {
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
      // saas 升级，版本更新和bug的折线图的init
      echarts.init(document.getElementById('saasUpgradeTrendChart'))
      echarts.init(document.getElementById('saasVersionTrendByResourcePoolChart'))
      echarts.init(document.getElementById('saasVersionTrendChart'))
      echarts.init(document.getElementById('saasProblemMonthChart'))
      echarts.init(document.getElementById('saasLargeProblemTypeChart'))
    },

    /**
     * 当查询之后，数据更新，根据新的数据更新升级趋势折线图的信息
     */
    updateSaaSUpgradeTrendLineChart() {
      // 对option的基础设置
      let option = {
        title: {
          top: '1%',
          left: '5%',
          text: this.resourcePoolSelected + '受理趋势',
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
          name: '升级时间',
          nameLocation: 'middle',
          nameGap: 25,
          nameTextStyle: {
            fontSize: 16,
          },
          type: 'time',
          axisLine: {
            onZero: false, // 不在y=0处对齐x轴
          }
        },
        yAxis: {
          name: '问题受理数量',
          nameLocation: 'middle',
          nameGap: 25,
          nameTextStyle: {
            fontSize: 16,
          },
          type: 'value',
          min: -1, // 设置y轴的最小值为-1，可以根据需要微调这个值, 让整个y轴不是从0开始向上移动
        },

        series: [],

      };

      // 对于每一条线数据的设置
      let versionData = []
      let currentVersion = []
      let legendData = []
      for (let i = 0; i < this.saasUpgradeLineChartData.length; i++) {
        // 版本号数据的取出，并且给当前版本号设置空值，那样第一个数据点就会显示版本号了
        versionData.push(this.saasUpgradeLineChartData[i].data.map((item) => item.version))
        currentVersion.push('')
        // 数据注入给echarts,定义data1因为不知道为什么label的formatter函数就访问不到this.saasUpgradeLineChartData, 而且将data1定义在for外面
        let data1 = this.saasUpgradeLineChartData[i].data
        // 
        let versionChangeData = data1.filter((item, index) => (index > 0 && item.version !== data1[index - 1].version) || (index === 0)).map(item => item)
        let series_1 = {
          name: this.saasUpgradeLineChartData[i].service,
          type: 'line',
          data: this.saasUpgradeLineChartData[i].data.map((item) => [item.x, item.y]),
          // 当每检测到版本号变动了，进行label的显示
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
            position: 'top',
          },
          markLine: {
            symbol: ['none', 'none'], //取消起始和结束箭头
            // 将数据进行过滤，只取每次变动的版本号的数据点，然后进行Markline虚线的展示
            data: versionChangeData.map((item) => {
              return {
                xAxis: item.x,
                lineStyle: {
                  type: 'dashed'
                },
                symbol: "none",
                label: {
                  show: false,
                }
              }
            }),
          }
        };
        option.series.push(series_1)
        // option.legend.data.push(this.saasUpgradeLineChartData[i].service)
        legendData.push(this.saasUpgradeLineChartData[i].service)
      }
      option.legend.data = legendData

      // 鼠标悬浮在数据点上的时候的设置
      option.tooltip = {
        trigger: 'axis',
        formatter: function (params) {
          const index = params[0].dataIndex; // 获取当前数据点的索引
          const xValue = params[0].value[0]; // x 值
          const yValue = params[0].value[1]; // y 值
          const version = versionData[params[0].seriesIndex][index]; // 获取数据点对应版本号
          // 使用legendData是因为取不到this.saasUpgradeLineChartData
          const func = legendData[params[0].seriesIndex]
          return `升级时间: ${xValue}<br/>受理数量: ${yValue}<br/>版本号: ${version}<br/>功能: ${func}`;
        }
      };

      let saasUpgradeTrendChart = echarts.getInstanceByDom(document.getElementById('saasUpgradeTrendChart'))
      if (saasUpgradeTrendChart) {
        saasUpgradeTrendChart.setOption(option, true)
      }

      console.log("updated updateSaaSUpgradeTrendLineChart : ", saasUpgradeTrendChart)

    },

    /**
     * 当查询之后，数据更新，更新重大事故数量和出错功能的饼状图的数据
     */
    updateSaaSLargeProblemTypeChart(chartData, chartTitle, chartElementId){
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
      searchValue['resourcePool'] = this.resourcePoolSelected.toString()
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
      } //结束for，完成日期的拼接
      
      this.searchSaaSServiceUpgradeTrend(searchValue)
      this.searchSaaSVersionUpgradeTrendByResoucePool(searchValue)
      this.searchSaaSVersionUpgradeTrend(searchValue)
      this.searchSaaSProblemByMonth(searchValue)
      this.searchSaaSLargeProblemByType(searchValue)
    },

    /**
     * @param {searchValue} searchValue 搜索参数的字典
     * @description 对升级趋势折线图的后端数据请求
     */
    async searchSaaSServiceUpgradeTrend(searchValue) {
      try {
        const response = await this.$http.get(
          '/api/CMC/workrecords/analysis_service_upgrade_trend?beginData=' +
          searchValue['beginData'] +
          '&endData=' +
          searchValue['endData'] +
          '&resourcePool=' +
          searchValue['resourcePool'] +
          '&function_name=' +
          searchValue['function_name']
        )
        this.saasUpgradeLineChartData = response.data.data
        this.updateSaaSUpgradeTrendLineChart()
        console.log('update local linechart data: ', this.saasUpgradeLineChartData)
      } catch (error) {
        console.log(error)
        this.$message.error('错了哦，仔细看错误信息弹窗')
        alert('失败' + error)
      }
    },

    /**
     * @param {searchValue} searchValue 搜索参数的字典
     * @description 对公有云指定资源池的版本和受理数量对比的查询
     */
     async searchSaaSVersionUpgradeTrendByResoucePool(searchValue) {
      try {
        const response = await this.$http.get(
          '/api/CMC/workrecords/analysis_version_problem_by_resource_pool?beginData=' +
          searchValue['beginData'] +
          '&endData=' +
          searchValue['endData'] +
          '&resourcePool=' +
          searchValue['resourcePool'] +
          '&function_name=' +
          searchValue['function_name']
        )
        this.saasVersionByResoucePoolBarChartData = response.data.data
        updateBarChartBasic(document, this.saasVersionByResoucePoolBarChartData, searchValue['resourcePool']+'SaaS版本受理及升级统计', "category", false, 'saasVersionTrendByResourcePoolChart')
        console.log('update local month bar chart data: ', this.saasVersionByResoucePoolBarChartData)

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
          '&resourcePool=' +
          searchValue['resourcePool'] +
          '&function_name=' +
          searchValue['function_name']
        )
        this.saasVersionBarChartData = response.data.data
        updateBarChartBasic(document, this.saasVersionBarChartData, 'SaaS全版本受理趋势', "category", false, 'saasVersionTrendChart')
        console.log('update local version linechart data: ', this.saasVersionBarChartData)

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
        updateBarChartBasic(document, this.saasProblemMonthChartData, searchValue['beginData'].slice(0,4)+'年SaaS月份受理统计', "category", false, 'saasProblemMonthChart')
        console.log('update local month bar chart data: ', this.saasProblemMonthChartData)

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
    async searchSaaSLargeProblemByType(searchValue) {
      try {
        const response = await this.$http.get(
          '/api/CMC/workrecords/analysis_saas_large_problem_by_function?beginData=' +
          searchValue['beginData'] +
          '&endData=' +
          searchValue['endData']
        )
        this.saasLargeProblemTypeChartData = response.data.data
        this.updateSaaSLargeProblemTypeChart(this.saasLargeProblemTypeChartData, "私有化重大故障问题分类", "saasLargeProblemTypeChart")
        console.log('update local saasLargeProblemTypeChartData data: ', this.saasLargeProblemTypeChartData)

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

.saasLargeProblemTypeChart {
  display: inline-block;
}

.saasLargeProblemTopTable {
  display: inline-block;
}

</style>