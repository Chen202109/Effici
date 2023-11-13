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
              <el-checkbox v-for="(item, index) in functionOptions[this.businessSelected]" :key="index"
                :label="item">{{ item }}</el-checkbox>
            </el-checkbox-group>
          </div>
        </div>
      </div>
    </div>

    <div class="saasUpgradeTrendChart" id="saasUpgradeTrendChart" :style="{ width: getMainPageWidth, height: '400px' }">
    </div>
    <div class="saasVersionTrendChart" id="saasVersionTrendChart" :style="{ width: getMainPageWidth, height: '400px' }">
    </div>
    <div class="saasProvinceAndFunctionChart" id="saasProvinceAndFunctionChart" :style="{ width: getMainPageWidth, height: '400px' }">
    </div>
    <div class="saasProvinceAndAgencyChart" id="saasProvinceAndAgencyChart" :style="{ width: getMainPageWidth, height: '400px' }">
    </div>

    <div></div>

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
      dateRange: [
        new Date(
          // new Date().getFullYear() + '-' + (new Date().getMonth() + 1) + '-01'
          new Date().getFullYear() + '-01-01'
        ),
        new Date(),
      ],

      saasUpgradeLineChartData: [],
      saasVersionBarChartData: [],
      saasProvinceBarChartData: [],
      saasProvinceAndAgencyChartData: [],
    }
  },
  // 计算页面刚加载时候渲染的属性
  computed: {
    data() { },
    getMainPageWidth: function () {
      // windows.screen.width返回屏幕宽度，减去侧边栏240px,减去container模型左右padding各20px和margin-right的10px,
      // 减去主页面各自15px的padding, 减去不知道那里vue自己设的30px, 减去主页面内元素和滚动条保持距离的padding-right的10px,
      return (window.screen.width - 240 - 20 * 2 - 10 - 15 * 2 - 30 - 10) + 'px'
    },
  },
  // 在初始化页面完成后,再对dom节点上图形进行相关绘制
  mounted() {
    console.log('升级汇报-分析升级', this.versionData);
    // 页面初始化后对checkbox,下拉列表组件添加初始值
    this.resourcePoolSelected = this.resourcePoolOptions[0];
    this.businessSelected.push(this.businessOptions[0]);
    this.functionSelected = this.functionOptions[this.businessSelected];
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

    // 用于使用echarts进行图标的基础绘制init
    drawLine() {
      // saas 升级，版本更新和bug的折线图的init
      let saasUpgradeTrendChart = echarts.init(document.getElementById('saasUpgradeTrendChart'))
      let saasVersionTrendChart = echarts.init(document.getElementById('saasVersionTrendChart'))
      let saasProvinceAndFunctionChart = echarts.init(document.getElementById('saasProvinceAndFunctionChart'))
      let saasProvinceAndAgencyChart = echarts.init(document.getElementById('saasProvinceAndAgencyChart'))
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
          text: 'SaaS公有云版本升级三线受理趋势',
          left: 'left'
        },
        legend: {
          top: '7%',
          data: []
        },
        grid: {
          top: '22%',
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

      console.log("updated echart upgrade linechart: ", saasUpgradeTrendChart)

    },

    /**
     * @param barChartData 整个图的数据数组
     * @param barChartTitle 这张图的标题
     * @param xAxisType x轴的坐标类型，有date，value，category等等
     * @param xAxisLabelNewLine 因为有些时候，x轴的坐标分类太多，比如当有30个以上的category的时候，导致x轴的有些标签会缺失，这个输入如果为true,会将偶数的label换行形成更多空间展示
     * @param chartElementId 对应的要更新的图表元素id
     * @description 当查询之后，数据更新，根据新的数据更新柱状图的基础配置。
     * 整个图的数据是一个大数组，里面包含的每个字典是：有属性seriesName, data。这里seriesName是该series的名字，data是该series的数据。
     * data是一个数组，里面同样也是多个字典，每个字典代表着一个数据点，格式为 {‘x’: "xxx", "y": "xxx", "aaa":"aaa", "bbb":"bbb"}
     * x和y的值是用于对应图的x和y轴的值，剩下的aaa，bbb等是其他可能多的需要添加的数据标签，但是再本基础配置方法中不做处理，只做x和y的对应。
     * xAxis的type为传入的参数，有date，value，category等等，yAxis的type默认为value,因为y轴一般是数值。
     */
    updateBarChartBasic(barChartData, barChartTitle, xAxisType, xAxisLabelNewLine, chartElementId){
      let xAxisData = barChartData[0].seriesData.map(item => item.x)
      // 看看是否要给x轴数据添加换行
      xAxisData =(xAxisLabelNewLine)? xAxisData.map((item, index) => (index%2===0)?item: '\n'+item): xAxisData
      let option = {
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
          top: '7%',
        },
        grid: {
          left: '3%',
          right: '3%',
          top: '22%',
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
            type: 'value'
          }
        ],
        series: []
      };

      for (let i = 0; i < barChartData.length; i++) {
        let series_1 = {
            name: barChartData[i].seriesName,
            type: 'bar',
            emphasis: {
              focus: 'series'
            },
            data: barChartData[i].seriesData.map(item=>item.y),
            label: {
              // 设置柱形图的数值
              show: true,
              position: 'top',
              align: 'center',
              formatter: '{c|{c}}次',
              rich: {
                c: {
                  // color: '#4C5058',
                  fontSize: 10,
                },
              }
            },
        }
        option.series.push(series_1)
      }

      let chart = echarts.getInstanceByDom(document.getElementById(chartElementId))
      if (chart) {
        chart.setOption(option, true)
      }

      console.log("updated echart : ", chart)
    },
    //   let xAxisData = this.saasProvinceBarChartData[0].data.map((item, index) => (index%2===0)?item.x: '\n'+item.x)

    //   let option = {
    //     title: {
    //       top: '1%',
    //       left: '5%',
    //       text: 'SaaS省份三线受理统计',
    //       left: 'left'
    //     },
    //     tooltip: {
    //       trigger: 'axis',
    //       axisPointer: {
    //         type: 'shadow'
    //       }
    //     },
    //     legend: {
    //       top: '7%',
    //     },
    //     grid: {
    //       left: '3%',
    //       right: '3%',
    //       top: '22%',
    //       bottom: '15%',
    //       containLabel: true
    //     },
    //     xAxis: [
    //       {
    //         type: 'category',
    //         axisLabel: { interval: 0 },
    //         data: xAxisData
    //       }
    //     ],
    //     yAxis: [
    //       {
    //         type: 'value'
    //       }
    //     ],
    //     series: []
    //   };

    //   for (let i = 0; i < this.saasProvinceBarChartData.length; i++) {
    //     let series_1 = {
    //         name: this.saasProvinceBarChartData[i].func,
    //         type: 'bar',
    //         emphasis: {
    //           focus: 'series'
    //         },
    //         data: this.saasProvinceBarChartData[i].data.map(item=>item.y),
    //         label: {
    //           // 设置柱形图的数值
    //           show: true,
    //           position: 'top',
    //           align: 'center',
    //           formatter: '{c|{c}}次',
    //           rich: {
    //             c: {
    //               // color: '#4C5058',
    //               fontSize: 10,
    //             },
    //           }
    //         },
    //     }
    //     option.series.push(series_1)
    //   }

    //   let saasProvinceChart = echarts.getInstanceByDom(document.getElementById('saasProvinceAndFunctionChart'))
    //   if (saasProvinceChart) {
    //     saasProvinceChart.setOption(option, true)
    //   }
    //   console.log("updated echart province barchart: ", saasProvinceChart)
    // }, 


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

      // 对升级趋势折线图的后端数据请求
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

      // 对版本趋势柱状图的后端数据请求
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
        // this.updateSaaSVersionTrendBarChart()
        this.updateBarChartBasic(this.saasVersionBarChartData,'SaaS版本三线受理趋势', "category", false, 'saasVersionTrendChart')
        console.log('update local version linechart data: ', this.saasVersionBarChartData)

      } catch (error) {
        console.log(error)
        this.$message.error('错了哦，仔细看错误信息弹窗')
        alert('失败' + error)
      }

      // 对省份受理数量柱状图的后端数据请求
      try {
        const response = await this.$http.get(
          '/api/CMC/workrecords/analysis_saas_function_by_province?beginData=' +
          searchValue['beginData'] +
          '&endData=' +
          searchValue['endData'] +
          '&resourcePool=' +
          searchValue['resourcePool'] +
          '&function_name=' +
          searchValue['function_name']
        )
        this.saasProvinceBarChartData = response.data.data
        // this.updateSaaSProvinceBarChart()
        this.updateBarChartBasic(this.saasProvinceBarChartData,'SaaS省份三线受理统计', "category", true, 'saasProvinceAndFunctionChart')
        console.log('update local province bar chart data: ', this.saasProvinceBarChartData)

      } catch (error) {
        console.log(error)
        this.$message.error('错了哦，仔细看错误信息弹窗')
        alert('失败' + error)
      }

      // 对省份受理数量和单位开通数量对比柱状图的后端数据请求
      try {
        const response = await this.$http.get(
          '/api/CMC/workrecords/analysis_saas_function_by_province_agency?beginData=' +
          searchValue['beginData'] +
          '&endData=' +
          searchValue['endData'] +
          '&resourcePool=' +
          searchValue['resourcePool'] +
          '&function_name=' +
          searchValue['function_name']
        )
        this.saasProvinceAndAgencyChartData = response.data.data
        this.updateBarChartBasic(this.saasProvinceAndAgencyChartData,'SaaS三线受理问题省份和单位开通数量对比', "category", true, 'saasProvinceAndAgencyChart')
        
        console.log('update local province and angency bar chart data: ', this.saasProvinceAndAgencyChartData)

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
}</style>