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

    <div style="margin: 5px 20px 5px 0;">
      <div class="saasDailyUpgradeTable">
        <p class="saasAnalysisTitle" style="margin: 10px 0;"> 公有云saas_v3/v4日常升级次数统计</p>
        <el-table :data="this.saasUpgradeProblemTypeTableData[0]['seriesData']"
          :header-cell-style="{ fontSize: '14px', background: 'rgb(64 158 255 / 65%)', color: '#696969', }"
          :row-style="{ height: '35px' }" :cell-style="upgradeTableCellStyle" border style="width: 100%">
          <el-table-column v-for="(value, key) in this.saasUpgradeProblemTypeTableData[0]['seriesData'][0]" :key="key"
            :prop="key" :label="key" :width="myColumnWidth(key)" align="center">
          </el-table-column>
        </el-table>
      </div>
      <div class="saasAddedUpgradeTable">
        <p class="saasAnalysisTitle" style="margin: 10px 0;"> 公有云saas_v3/v4增值升级次数统计</p>
        <el-table :data="this.saasUpgradeProblemTypeTableData[1]['seriesData']"
          :header-cell-style="{ fontSize: '14px', background: 'rgb(64 158 255 / 65%)', color: '#696969', }"
          :row-style="{ height: '35px' }" :cell-style="upgradeTableCellStyle" border style="width: 100%">
          <el-table-column v-for="(value, key) in this.saasUpgradeProblemTypeTableData[1]['seriesData'][0]" :key="key"
            :prop="key" :label="key" :width="myColumnWidth(key)" align="center">
          </el-table-column>
        </el-table>
      </div>
    </div>

    <div style="height: 20px;"></div>

    <div style="margin: 5px 20px 5px 0;">
      <div class="ticketFolderDailyUpgradeTable">
        <p class="saasAnalysisTitle" style="margin: 10px 0;"> {{this.ticketFolderUpgradeProblemTypeTableData[0]["seriesName"]}}</p>
        <el-table :data="this.ticketFolderUpgradeProblemTypeTableData[0]['seriesData']"
          :header-cell-style="{ fontSize: '14px', background: 'rgb(64 158 255 / 65%)', color: '#696969', }"
          :row-style="{ height: '35px' }" :cell-style="upgradeTableCellStyle" border style="width: 100%">
          <el-table-column v-for="(value, key) in this.ticketFolderUpgradeProblemTypeTableData[0]['seriesData'][0]" :key="key"
            :prop="key" :label="key" :width="myColumnWidth(key)" align="center">
          </el-table-column>
        </el-table>
      </div>
    </div>


    <div style="height: 20px;"></div>

    <div class="saasUpgradeTrendChart" id="saasUpgradeTrendChart" :style="{ width: getPageWidth + 'px', height: '400px' }">
    </div>
    <div class="saasVersionTrendByResourcePoolChart" id="saasVersionTrendByResourcePoolChart"
      :style="{ width: getPageWidth + 'px', height: '400px' }">
    </div>

  </div>
</template>


<script>
import { getMainPageWidth, columnWidth } from '@/utils/layoutUtil'
import { updateBarChartBasic } from '@/utils/echartBasic'

// 引入基本模板
let echarts = require("echarts/lib/echarts");
// 引入提示框和title组件
require("echarts/lib/component/tooltip");
require("echarts/lib/component/title");

export default {
  name: 'AnalysisUpgradeTrend',
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

      // 公有云saas_v4日常和增值升级统计，第一个元素是日常的表格的数据，第二个元素是增值表格的数据
      saasUpgradeProblemTypeTableData: [{ 'seriesName': "", 'seriesData': [] }, { 'seriesName': "", 'seriesData': [] }],

      // 票夹的日常和增值升级统计，第一个元素是日常的表格的数据，第二个元素是增值表格的数据
      ticketFolderUpgradeProblemTypeTableData: [{ 'seriesName': "", 'seriesData': [] }, { 'seriesName': "", 'seriesData': [] }],


      // 这个页面各类图的数据
      saasUpgradeLineChartData: [],
      saasVersionByResoucePoolBarChartData: [],
    }
  },
  // 计算页面刚加载时候渲染的属性
  computed: {
    data() { },
    getPageWidth: getMainPageWidth
  },
  // 在初始化页面完成后,再对dom节点上图形进行相关绘制
  mounted() {
    // 页面初始化后对checkbox,下拉列表组件添加初始值
    this.resourcePoolSelected = this.resourcePoolOptions[0];
    this.businessSelected.push(this.businessOptions[0]);
    this.functionSelected = this.functionOptions[this.businessSelected].slice(0, 3);
    // 对图标进行一个初始化
    this.drawLine();
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

    /**
     * 计算el-table列的宽度
     */
    myColumnWidth(key, tableName) {
      return columnWidth(key)
    },

    upgradeTableCellStyle(row) {
      let style = ''
      // if (row.rowIndex === this.saasUpgradeData[0].length - 1) {
      //   style = 'background: rgb(253 238 32 / 20%);'
      // }
      style += 'font-size: 14px; '
      return style
    },

    /**
     * 用于使用echarts进行图标的基础绘制init
     */
    drawLine() {
      // saas 升级，版本更新和bug的折线图的init
      echarts.init(document.getElementById('saasUpgradeTrendChart'))
      echarts.init(document.getElementById('saasVersionTrendByResourcePoolChart'))
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
      saasUpgradeTrendChart && saasUpgradeTrendChart.setOption(option, true)

      console.log("updated updateSaaSUpgradeTrendLineChart : ", saasUpgradeTrendChart)

    },

    /**
     * 按下查询按钮之后异步查询更新页面图标数据。
     */
    async search() {
      // 触发查询事件，根据日期条件进行查询
      var searchValue = {} // 存放筛选条件信息
      searchValue['resourcePool'] = this.resourcePoolSelected.toString()
      searchValue['functionName'] = this.functionSelected.toString()
      // 获取年、月、日，进行拼接
      for (let i = 0; i < this.dateRange.length; i++) {
        var year = this.dateRange[i].getFullYear()
        var month = ('0' + (this.dateRange[i].getMonth() + 1)).slice(-2)
        var day = ('0' + this.dateRange[i].getDate()).slice(-2)
        searchValue[(i == 0) ? "beginData" : "endData"] = year + "-" + month + "-" + day;
      } //结束for，完成日期的拼接
      // 告诉后端是搜索行业侧的还是票夹侧的
      searchValue['systemLabel'] = [1,2]

      this.searchSaasUpgradeProblemTypeTable(searchValue)
      this.searchSaaSServiceUpgradeTrend(searchValue)
      this.searchSaaSVersionUpgradeTrendByResoucePool(searchValue)
      this.searchTicketFolderUpgradeProblemTypeTable(searchValue)
    },

    /**
     * @param {searchValue} searchValue 搜索参数的字典
     * @description 查询更新升级和所属问题分类的数据信息的后端数据请求
     */
    async searchSaasUpgradeProblemTypeTable(searchValue) {
      this.$http.get(
        '/api/CMC/workrecords/upgrade/analysis_saas_upgrade_problem_type?beginData=' +
        searchValue['beginData'] +
        '&endData=' +
        searchValue['endData'] +
        '&systemLabel=' +
        searchValue['systemLabel'][0]
      ).then(response => {
        this.saasUpgradeProblemTypeTableData = response.data.data
        console.log('update local saasUpgradeProblemTypeTableData data: ', response.data.data)
      }).catch((error) => {
        console.log(error)
        console.log(error.response.data.message)
        this.$message.error(error.response.data.message)
      })
    },

    /**
     * @param {searchValue} searchValue 搜索参数的字典
     * @description 对升级趋势折线图的后端数据请求
     */
    async searchSaaSServiceUpgradeTrend(searchValue) {
      this.$http.get(
          '/api/CMC/workrecords/upgrade/analysis_saas_service_upgrade_trend?beginData=' +
          searchValue['beginData'] +
          '&endData=' +
          searchValue['endData'] +
          '&resourcePool=' +
          searchValue['resourcePool'] +
          '&functionName=' +
          searchValue['functionName']
        ).then(response => {
          this.saasUpgradeLineChartData = response.data.data
          this.updateSaaSUpgradeTrendLineChart()
          console.log('update local linechart data: ', this.saasUpgradeLineChartData)
        }).catch((error) => {
          console.log(error.response.data.message)
          this.$message.error(error.response.data.message)
        })
    },

    /**
     * @param {searchValue} searchValue 搜索参数的字典
     * @description 对公有云指定资源池的版本和受理数量对比的查询
     */
    async searchSaaSVersionUpgradeTrendByResoucePool(searchValue) {
      this.$http.get(
          '/api/CMC/workrecords/upgrade/analysis_saas_version_problem_by_resource_pool?beginData=' +
          searchValue['beginData'] +
          '&endData=' +
          searchValue['endData'] +
          '&resourcePool=' +
          searchValue['resourcePool'] +
          '&functionName=' +
          searchValue['functionName']
        ).then(response => {
          this.saasVersionByResoucePoolBarChartData = response.data.data
          updateBarChartBasic(document, this.saasVersionByResoucePoolBarChartData, searchValue['resourcePool'] + 'SaaS版本受理及升级统计', "category", false, true, 'saasVersionTrendByResourcePoolChart')
          console.log('update local month bar chart data: ', this.saasVersionByResoucePoolBarChartData)
        }).catch((error) => {
          console.log(error)
          console.log(error.response.data.message)
          this.$message.error(error.response.data.message)
        })
    },

    /**
     * @param {searchValue} searchValue 搜索参数的字典
     * @description 查询更新升级和所属问题分类的数据信息的后端数据请求
     */
     async searchTicketFolderUpgradeProblemTypeTable(searchValue) {
      this.$http.get(
        '/api/CMC/workrecords/upgrade/analysis_saas_upgrade_problem_type?beginData=' +
        searchValue['beginData'] +
        '&endData=' +
        searchValue['endData'] +
        '&systemLabel=' +
        searchValue['systemLabel'][1]
      ).then(response => {
        this.ticketFolderUpgradeProblemTypeTableData = response.data.data
        console.log('update local ticketFolderUpgradeProblemTypeTableData data: ', response.data.data)
      }).catch((error) => {
        console.log(error.response.data.message)
        this.$message.error(error.response.data.message)
      })
    },
  }
}
</script>


<style scoped>
.saasAnalysisTitle {
  color: #3398DB;
  font-size: 18px;
  margin: 5px 10px 5px 0;
}

.saasDailyUpgradeTable, .ticketFolderDailyUpgradeTable {
  width: 50%;
  display: inline-block;
  margin: 0 10px 0 0;
}

.saasAddedUpgradeTable, .ticketFolderAddedUpgradeTable {
  width: 48%;
  display: inline-block;
  margin: 0 0 0 10px;
  float: right;
}

.el-dropdown-link {
  cursor: pointer;
  color: #409EFF;
}

.el-icon-arrow-down {
  font-size: 12px;
}
</style>