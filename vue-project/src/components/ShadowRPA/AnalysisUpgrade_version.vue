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
    <div class="saasProvinceAndFunctionChart" id="saasProvinceAndFunctionChart" :style="{ width: getMainPageWidth+ 'px', height: '400px' }">
    </div>
    <div class="saasProvinceAndFunctionChartSplit" id="saasProvinceAndFunctionChartSplit">
      <!-- 因为省份和功能会产生太多柱子，所以对省份进行一个切割，分成多张图来展现，注意，v-for这边生成的i是从1开始，所以id的末尾是1不是0 -->
      <div v-for="i in provinceSplitNum" 
         :class="'saasProvinceAndFunctionChart' + i" 
         :id="'saasProvinceAndFunctionChart' + i"
         :style="{ width: getMainPageWidth+ 'px', height: '400px' }">
      </div>
    </div>
    <div class="saasProvinceAndAgencyChart" id="saasProvinceAndAgencyChart" :style="{ width: getMainPageWidth+ 'px', height: '400px' }">
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
      // 将省份和出错功能对比的柱形图分割成几个子图
      provinceSplitNum : 2,
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
      echarts.init(document.getElementById('saasProvinceAndFunctionChart'))
      echarts.init(document.getElementById('saasProvinceAndAgencyChart'))
      echarts.init(document.getElementById('saasProblemMonthChart'))
      echarts.init(document.getElementById('saasLargeProblemTypeChart'))
      // 因为是使用v-for生成的元素，所以使用this.$nextTick来进行延迟，否则可能会出现还没渲染元素就init的情况
      this.$nextTick(() => {for (let i = 0; i < this.provinceSplitNum; i++) echarts.init(document.getElementById('saasProvinceAndFunctionChart'+(i+1)))})
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
    updateBarChartBasic(barChartData, barChartTitle, xAxisType, xAxisLabelNewLine, chartElementId) {
      // 拿到x轴的数据
      let xAxisData = barChartData[0].seriesData.map(item => item.x)
      // 将如果所有项都是0的x轴的值去掉
      let removeList = []
      xAxisData.forEach((item) => {
        let count = 0
        barChartData.forEach(({ seriesData }) => { count = (seriesData.find(ele => ele.x === item).y === 0) ? count + 1 : count })
        if (count === barChartData.length) removeList.push(item)
      })
      xAxisData = xAxisData.filter(item => !removeList.includes(item))

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
            type: 'value'
          }
        ],
        series: []
      };

      // 根据数据对图标添加series
      this.normalBarChartAddingSeries(barChartData, option)

      // 看看是否要给x轴数据添加换行
      xAxisData = (xAxisLabelNewLine) ? xAxisData.map((item, index) => (index % 2 === 0) ? item : '\n' + item) : xAxisData
      option.xAxis[0].data = xAxisData

      let chart = echarts.getInstanceByDom(document.getElementById(chartElementId))
      if (chart) {
        chart.setOption(option, true)
      }

      console.log("updated " + chartElementId + " echart : ", chart)
    },

    /**
     * 将柱状图的数组信息循环添加进入柱状图的series中
     * @param {barChartData} barChartData 后端返回的包含柱状图所有信息的一个数组
     * @param {option} option 柱状图的option
     */
    normalBarChartAddingSeries(barChartData, option) {
      // 指定了柱子的15种颜色，因为不设置的话echarts默认超过9个颜色会开始循环，所以扩大一点，变成15个颜色开始循环
      let colors = ["#5470C6", "#91CC75", "#FAC858", "#EE6666", "#73C0DE", "#3BA272", "#fc8452", "#a26dba", "#ea7ccc", "#ffe630", "#00A0AF", "#DB643E", "#EA8D89", "#F4B2E5", "#F03A6A"]
      for (let i = 0; i < barChartData.length; i++) {
        let series_1 = {
          name: barChartData[i].seriesName,
          type: 'bar',
          barMaxWidth: 30,
          emphasis: {
            focus: 'series'
          },
          // data: barChartData[i].seriesData.map(item=>item.y),
          data: barChartData[i].seriesData.filter((item) => option.xAxis[0].data.includes(item.x)).map(item => item.y),
          itemStyle: {
            color : colors[i%colors.length]
          },
          label: {
            // 设置柱形图的数值
            show: true,
            position: 'top',
            align: 'center',
            // formatter: function (params){
            //   return (params.value===0)?"":params.value+"次"
            // },
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
    },

    /**
     * 当查询之后，数据更新，更新省份受理与单位数量对比的省份数据柱状图和单位数量的折线数据更新
     */
    updateSaaSProvinceAndAgencyBarChart(barChartData, barChartTitle, xAxisType, xAxisLabelNewLine, chartElementId){
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
              data: barChartData[0].seriesData.map(item=>item.y),
            },
            {
              name: barChartData[1].seriesName,
              type: 'bar',
              yAxisIndex: 0,
              data: barChartData[1].seriesData.map(item=>item.y),
            },
            {
              name: barChartData[2].seriesName,
              type: 'line',
              yAxisIndex: 1,
              data: barChartData[2].seriesData.map(item=>item.y),
            }
        ]
      }

      // 看看是否要给x轴数据添加换行
      xAxisData = (xAxisLabelNewLine) ? xAxisData.map((item, index) => (index % 2 === 0) ? item : '\n' + item) : xAxisData
      option.xAxis[0].data = xAxisData

      let chart = echarts.getInstanceByDom(document.getElementById(chartElementId))
      // 现在是添加属性，所以不用replace设成true，直接setOption就行
      chart&&chart.setOption(option, true)

      console.log("updated saasProvinceAndAgencyChart echart: ", chart)
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
      this.searchSaaSFunctionByProvince(searchValue)
      this.searchSaaSProblemByProvinceAgency(searchValue)
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
        this.updateBarChartBasic(this.saasVersionByResoucePoolBarChartData, searchValue['resourcePool']+'SaaS版本受理及升级统计', "category", false, 'saasVersionTrendByResourcePoolChart')
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
        this.updateBarChartBasic(this.saasVersionBarChartData, 'SaaS全版本受理趋势', "category", false, 'saasVersionTrendChart')
        console.log('update local version linechart data: ', this.saasVersionBarChartData)

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

        this.updateBarChartBasic(this.saasProvinceBarChartData, 'SaaS省份三线受理统计', "category", true, 'saasProvinceAndFunctionChart')
        console.log('update local province bar chart data: ', this.saasProvinceBarChartData)
        
        let interval = this.saasProvinceBarChartData[0]["seriesData"].length/this.provinceSplitNum
        // 要分成几张图的数据，进行遍历循环，给柱状图添加数据。
        for (let i = 0; i < this.provinceSplitNum; i++){
          let splitData = []
          this.saasProvinceBarChartData.forEach((item)=> {splitData.push({seriesName: item.seriesName, seriesData: item.seriesData.slice(i*interval,(i+1)*interval)})})
          // 将数据注入柱状图内，i+1是因为元素在使用v-for生成的时候，v-for的i是从1开始，这里是0开始，所以使用i+1来获取相同的id
          this.updateBarChartBasic(splitData, 'SaaS省份三线受理统计(子集'+(i+1)+')', "category", false, 'saasProvinceAndFunctionChart'+(i+1))
          let chart = echarts.getInstanceByDom(document.getElementById('saasProvinceAndFunctionChart'+(i+1)))
          chart.setOption({
            yAxis : {
              type : "value",
              max: Math.ceil( yMax/10 ) *10
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
        // this.updateBarChartBasic(this.saasProvinceAndAgencyChartData, 'SaaS全国各省受理统计', "category", true, 'saasProvinceAndAgencyChart')
        this.updateSaaSProvinceAndAgencyBarChart(this.saasProvinceAndAgencyChartData, 'SaaS全国各省受理统计', "category", true, 'saasProvinceAndAgencyChart')
        console.log('update local province and angency bar chart data: ', this.saasProvinceAndAgencyChartData)

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
        this.updateBarChartBasic(this.saasProblemMonthChartData, searchValue['beginData'].slice(0,4)+'年SaaS月份受理统计', "category", false, 'saasProblemMonthChart')
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
          '/api/CMC/workrecords/analysis_saas_large_problem_by_province_and_function?beginData=' +
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