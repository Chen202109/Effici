<template>
  <!-- 所有的内容要被根节点包含起来-->
  <div id="news">
    <div style="margin: 15px 0">
      <template>
        <div class="block">
          <span class="demonstration">分析范围： </span>
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期"
            end-placeholder="结束日期">
          </el-date-picker>
          <el-button type="primary" @click="search">查询</el-button>
          <el-button type="primary" @click='exportAnalysePage'>导出</el-button>
          <el-button type="primary" @click='exportAnalysePage_1'>导出测试</el-button>
        </div>
      </template>
    </div>

    <div style="margin: 15px 0">
      <!-- 临时放入table 组件 style="font-size: 10px; width: 100%"-->
      <template>
        <!-- 周末要发的受理信息数据-->
        <saasProblemTable :saasProblemTableData="analysisData['tableData']"></saasProblemTable>
      </template>
    </div>

    <div style="height: 20px;"></div>

    <div id='saasProblemCharts'>
      <!-- 放入Echarts 可视化图形 组件 -->
      <div class="myChart" id="myChart" :style="{ width: getInlineChartsWidth, height: '400px' }"></div>
      <div class="saasProblemPieChart" id="saasProblemPieChart" :style="{ width: getInlineChartsWidth, height: '400px' }"></div>
    </div>

    <div class="clearFloat"></div>

    <div style="height: 20px;"></div>

    <p class="saasAnalysisTitle"> SaaS各版本处理汇总</p>
    <div style="margin: 15px 20px 15px 0;">
      <el-table :data="saasProblemTypeInVersions"
        :header-cell-style="{ fontSize: '14px', background: 'rgb(64 158 255 / 65%)', color: '#696969', }"
        :row-style="{ height: '25px' }" :cell-style="saasProblemTypeInVersionTableCellStyle" border style="width: 100%">
        <el-table-column v-for="(value, key) in saasProblemTypeInVersions[0]" :key="key" :prop="key"
          :label="key.replace(/\_/g, '.')" :width="columnWidth(key)" align="center">
        </el-table-column>
      </el-table>
    </div>

    <div style="height: 20px;"></div>

    <p class="saasAnalysisTitle"> license受理数据</p>
    <!-- 放入license的数据组件 -->
    <div style="margin: 15px 0">
      <license :licenseData="analysisData['licenseData']"></license>
    </div>

    <div style="height: 20px;"></div>


    <!-- 放入upgrade 资源池升级数据组件 -->
    <div style="margin: 5px 20px 5px 0;">
      <div>
        <div class="dailyUpgradeTable">
          <p class="saasAnalysisTitle" style="margin: 10px 0;"> 公有云saas_v4日常升级统计</p>
          <el-table :data="this.saasUpgradeData[0]"
            :header-cell-style="{ fontSize: '14px', background: 'rgb(64 158 255 / 65%)', color: '#696969', }"
            :row-style="{ height: '35px' }" 
            :cell-style="upgradeTableCellStyle" 
            border
            style="width: 100%">
            <el-table-column v-for="(value, key) in this.saasUpgradeData[0][0]" :key="key" :prop="key" :label="key"
              :width="columnWidth(key)" align="center">
            </el-table-column>
          </el-table>
        </div>
        <div class="addedUpgradeTable">
          <p class="saasAnalysisTitle" style="margin: 10px 0;"> 公有云saas_v4增值升级统计</p>
          <el-table :data="this.saasUpgradeData[1]"
            :header-cell-style="{ fontSize: '14px', background: 'rgb(64 158 255 / 65%)', color: '#696969', }"
            :row-style="{ height: '35px' }" 
            :cell-style="upgradeTableCellStyle" 
            border
            style="width: 100%">
            <el-table-column v-for="(value, key) in this.saasUpgradeData[1][0]" :key="key" :prop="key" :label="key"
              :width="columnWidth(key)" align="center">
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>


  </div>
</template>

<script>
import saasProblemTable from '@/components/ShadowRPA/AnalysisData_saasProblemTable.vue'
import license from '@/components/ShadowRPA/AnalysisData_license.vue'
import upgrade from '@/components/ShadowRPA/AnalysisData_upgrade.vue'
import html2pdf from 'html2pdf.js'


// // 导出功能
// const fs = require('fs')
// const PDFDocument = require('pdfkit')

// 引入基本模板
let echarts = require('echarts/lib/echarts')
// 引入柱状图组件
require('echarts/lib/chart/bar')
// 引入提示框和title组件
require('echarts/lib/component/tooltip')
require('echarts/lib/component/title')
export default {
  name: 'AnalysisData',
  components: {
    license,
    upgrade,
    saasProblemTable
  },
  data() {
    return {
      tableTitle: [
        { prop: 'total', label: '受理合计' },
        { prop: 'report', label: '报表功能' },
        { prop: 'openbill', label: '开票功能' },
        { prop: 'licenseReset', label: 'license重置' },
        { prop: 'added', label: '增值服务' },
        { prop: 'collection', label: '收缴业务' },
        { prop: 'exchange', label: '通知交互' },
        { prop: 'writeoff', label: '核销功能' },
        { prop: 'billManagement', label: '票据管理' },
        { prop: 'security', label: '安全漏洞' },
        { prop: 'print', label: '打印功能' },
        { prop: 'datasync', label: '数据同步' },
        { prop: 'inverse', label: '反算功能' },
        { prop: 'opening', label: '单位开通' },
        { prop: 'softbug', label: '缺陷合计' },
      ],
      saasProblemTypeInVersions: [
        {
          "问题分类": "产品bug",
        },
        {
          "问题分类": "实施配置",
        },
        {
          "问题分类": "异常数据处理",
        },
      ],
      saasUpgradeData: [
        [
          {
            " ": "升级次数",
          },
          {
            " ": "缺陷",
          },
          {
            " ": "需求",
          },
          {
            " ": "优化",
          },
        ],
        [
          {
            " ": "升级次数",
          },
          {
            " ": "缺陷",
          },
          {
            " ": "需求",
          },
          {
            " ": "优化",
          },
        ],
      ],
      //查询日期
      dateRange: [
        new Date(
          new Date().getFullYear() + '-' + (new Date().getMonth() + 1) + '-01'
        ),
        new Date(),
      ],
      // 通过this.$http.get 请求analysisselect 返回的 分析analysis 数据data
      analysisData: {
        // tableData 受理表格数据
        tableData: [
          {
            added: '0',
            billManagement: '0',
            collection: '0',
            datasync: '0',
            exchange: '0',
            inverse: '0',
            licenseReset: '0',
            openbill: '0',
            opening: '0',
            print: '0',
            report: '0',
            security: '0',
            softversion: '0',
            total: '0',
            writeoff: '0',
            softbug: '0',
          },
        ],
        // upgradeData 升级计划表格的数据
        upgradeData: [

        ], // 升级表格数据


        // licenseData license表格的数据
        licenseData: [
          {
            北京: 999,
            山西: 99,
            内蒙古: 99,
            辽宁: 99,
            吉林: 99,
            黑龙江: 99,
            上海: 99,
            安徽: 99,
            福建: 99,
            江西: 999,
            山东: 99,
            河南: 99,
            湖北: 99,
            广东: 99,
            广西: 99,
            海南: 99,
            重庆: 99,
            四川: 99,
            贵州: 999,
            云南: 99,
            西藏: 99,
            陕西: 99,
            甘肃: 99,
            青海: 99,
            宁夏: 99,
            新疆: 99,
          },
        ], // license表格数据
      },
    }
  },
  // 计算页面刚加载时候渲染的属性
  computed: {
    data() { },
    getInlineChartsWidth: function(){
      // windows.screen.width返回屏幕宽度，减去侧边栏240px,减去container模型左右padding各20px和margin-right的10px,
      // 减去主页面各自15px的padding, 减去不知道那里vue自己设的30px, 减去主页面内元素和滚动条保持距离的padding-right的10px,
      return (window.screen.width-240-20*2-10-15*2-30-10)/2+'px'
    },
  },
  // 在初始化页面完成后,再对dom节点上图形进行相关绘制
  mounted() {
    this.drawLine()
  },

  methods: {
    // 进行Echarts的图形绘制
    drawLine() {
      // 基于准备好的dom，初始化echarts实例
      let myChart = echarts.init(document.getElementById('myChart'))
      let saasProblemPieChart = echarts.init(document.getElementById('saasProblemPieChart'))

      // 绘制柱形图形
      myChart.setOption({
        color: ['#3398DB'], // 设置柱形图颜色
        //设置 title 的 字体大小 和颜色
        title: {
          text: 'SaaS各版本受理汇总',
          left: 'left',
          top: '1%',
          textStyle: {
            fontSize: 18,
            fontWeight: 'normal',
            fontStyle: 'normal',
            color: '#3398DB',
          },
        },
        tooltip: {
          //设置鼠标悬停提示框的位置。
          //   trigger: 'axis',
          //   position: [20, 20]
          //   // 等价于
          //   // position: ['20px', '20px']
        },
        xAxis: {
          data: [
            'V3',
            'V4.0.4.7',
            'V4.3.1.0',
            'V4.3.1.2',
            'V4.0.4.6',
            'V4.0.4.5',
          ],
        },
        yAxis: {},
        grid: {
          left: '5%',
          right: '5%',
          top: '11%',
          bottom: '7%',
        },
        series: [
          {
            name: '数量',
            type: 'bar',
            data: [5, 20, 36, 10, 10, 20],
            // label 是说是否显示柱形图上的数值，position 表示数值的位置
            label: {
              show: true,
              position: 'top',
              //字体大小
              fontSize: 14,
            },
          },
        ],
      }),

      saasProblemPieChart.setOption({
        title: {
          text: 'SaaS受理问题分类',
          left: 'left',
          top: '1%',
          textStyle: {
            fontSize: 18,
            fontWeight: 'normal',
            fontStyle: 'normal',
            color: '#3398DB',
          },
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },

        series: [
          {
            name: 'Access From',
            type: 'pie',
            selectedMode: 'single',
            radius: [0, '40%'],
            top: "1%",
            label: {
              show: true, // 是否显示标签
              formatter: '{b}\n{c}次 \n {d}%',
              position: 'inside', // 设置标签位置为内部
              fontSize: 12, // 设置标签字体大小为14px
              color: '#000000',
            },
            labelLine: {
              show: false
            },
            data: [
              { value: 10, name: '程序bug', },
              { value: 19, name: '实施配置', },
              { value: 6, name: '异常情况处理', }
            ]
          },
          {
            name: 'Access From',
            type: 'pie',
            radius: ['50%', '65%'],
            top: "1%",
            left: 'center',
            width: 600,
            labelLine: {
              length: 15,
              length2: 0,
              maxSurfaceAngle: 80
            },
            label: {
              alignTo: 'edge',
              formatter: '{b|{b}：}{c}次 {per|{d}%}  ',
              minMargin: 5,
              edgeDistance: 10,
              lineHeight: 15,
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
                },
              }
            },
            labelLayout: function (params) {
              const isLeft = params.labelRect.x < myChart.getWidth() / 2;
              const points = params.labelLinePoints;
              // Update the end point.
              points[2][0] = isLeft
                ? params.labelRect.x
                : params.labelRect.x + params.labelRect.width;
                points[1][1] = params.labelRect.y+params.labelRect.height
                points[2][1] = params.labelRect.y+params.labelRect.height
              return {
                labelLinePoints: points
              };
            },
            data: [
              { value: 3, name: 'report' },
              { value: 5, name: 'openbill' },
              { value: 6, name: 'licenseReset' },
              { value: 2, name: 'added' },
              { value: 3, name: 'collection' },
              { value: 1, name: 'exchange' },
              { value: 6, name: 'writeoff' },
              { value: 1, name: 'billManagement' },
              { value: 0, name: 'security' },
              { value: 0, name: 'print' },
              { value: 2, name: 'datasync' },
              { value: 2, name: 'inverse' },
              { value: 8, name: 'opening' }
            ]
          }
        ]
      })
    },

    saasTableCellStyle(row) {//根据情况显示背景色
      let style = ''
      if (row.rowIndex === this.analysisData["tableData"].length - 1) {
        style = 'background: rgb(253 238 32 / 20%);'
      }
      if (row.column.label === "程序版本") {
        style = 'background: rgb(64 158 255 / 50%);'
      } else if (row.column.label === "受理合计") {
        style = 'background: rgb(253 238 32 / 20%); color: red; '
      } else if (row.column.label === "缺陷合计") {
        style = 'background: rgba(245, 108, 108, 0.41); color: blue; '
      }
      style += 'font-size: 14px; '
      return style
    },


    saasProblemTypeInVersionTableCellStyle(row) {
      let style = ''
      if (row.column.label === "合计") {
        style = 'background: rgb(253 238 32 / 20%); color: red; '
      }
      style += 'font-size: 14px; '
      return style
    },

    upgradeTableCellStyle(row) {
      let style = ''
      if (row.rowIndex === this.saasUpgradeData[0].length - 1) {
        style = 'background: rgb(253 238 32 / 20%);'
      }
      style += 'font-size: 14px; '
      return style
    },

    // 计算el-table列的宽度
    columnWidth(key) {
      key= key.replace(/_/g, '').replace(/[^\w\u4e00-\u9fa50-9]/g, "")
      let widthDict = {
        2: 55,
        3: 65,
        4: 75,
        5: 85,
        6: 110,
        10: 130,
      }
      let width
      if (key === "问题分类") {
        width = 110
      } else if (key.length in widthDict){
        width = widthDict[key.length]
      }
      return width
    },


    // 进行 查询 事件,因为axios是异步的请求，所以会先处理数据，空闲了才处理异步数据
    async search() {
      // 触发查询事件，根据日期条件进行查询
      var searchValue = {} // 存放筛选条件信息
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

      // 使用axios发送请求 获取license的申请数据
      try {
        const response = await this.$http.get(
          '/api/CMC/workrecords/analysisselect?beginData=' +
          searchValue['beginData'] +
          '&endData=' +
          searchValue['endData']
        )
        console.log('获得this.analysisData为', response.data.data)
        this.analysisData = response.data.data // 这里不能将整个data赋过去，会造成其他数据被覆盖

        // 清空原来数据，根据每一次搜索的数据重新生成
        this.saasProblemTypeInVersions = [
        {
          "问题分类": "产品bug",
        },
        {
          "问题分类": "实施配置",
        },
        {
          "问题分类": "异常数据处理",
        },
      ]

        for (const item of this.analysisData['tableData']) {
          this.saasProblemTypeInVersions[0][item['softversion'].replace(/\./g, '_')] = item['softbug']
          this.saasProblemTypeInVersions[1][item['softversion'].replace(/\./g, '_')] = item['sspz']
          this.saasProblemTypeInVersions[2][item['softversion'].replace(/\./g, '_')] = item['ycsjcl']
        }


        //for循环计算license申请的 合计数
        let license_total = 0
        for (const dict of this.analysisData['licenseData']) {
          // 遍历字典的键
          for (const value of Object.values(dict)) {
            // 遍历字典的值
            if (typeof value === 'number') {
              license_total += value
            } // 如果是数字，则相加, 目的是为排除开汉字 申请单位数
          }
        }
        this.analysisData['licenseData'][0]['合计'] = license_total //字典加入合计数


        // 清空原来的数据，根据每一次搜索重新生成表格
        this.saasUpgradeData = [
        [
          {
            "saas_v4标准产品": "缺陷",
          },
          {
            "saas_v4标准产品": "需求",
          },
          {
            "saas_v4标准产品": "优化",
          },
          {
            "saas_v4标准产品": "升级次数合计",
          },
        ],
        [
          {
            "saas_v4增值产品": "缺陷",
          },
          {
            "saas_v4增值产品": "需求",
          },
          {
            "saas_v4增值产品": "优化",
          },
          {
            "saas_v4增值产品": "升级次数合计",
          },
        ],
      ]

        let dailyUpgradeTableData = this.analysisData["upgradeData"].filter(item => item.upgradetype === '日常')
        let addedUpgradeTableData = this.analysisData["upgradeData"].filter(item => item.upgradetype === '增值')

        // // 计算upgrade的合计行
        // let upgrade_total = {
        //   "resourcepool": "合计",
        //   "upgradetype": "",
        //   "升级次数": 0,
        //   "缺陷": 0,
        //   "需求": 0,
        //   "优化": 0
        // }

        // for (const item in dailyUpgradeTableData) {
        //   upgrade_total["升级次数"] += parseInt(dailyUpgradeTableData[item]["升级次数"])
        //   upgrade_total["缺陷"] += parseInt(dailyUpgradeTableData[item]["缺陷"])
        //   upgrade_total["需求"] += parseInt(dailyUpgradeTableData[item]["需求"])
        //   upgrade_total["优化"] += parseInt(dailyUpgradeTableData[item]["优化"])
        // }
        // // 将合计行放入dailyUpgradeTableData中
        // dailyUpgradeTableData.push(upgrade_total)

        // upgrade_total = {
        //   "resourcepool": "合计",
        //   "upgradetype": "",
        //   "升级次数": 0,
        //   "缺陷": 0,
        //   "需求": 0,
        //   "优化": 0
        // }

        // for (const item in addedUpgradeTableData) {
        //   upgrade_total["升级次数"] += parseInt(addedUpgradeTableData[item]["升级次数"])
        //   upgrade_total["缺陷"] += parseInt(addedUpgradeTableData[item]["缺陷"])
        //   upgrade_total["需求"] += parseInt(addedUpgradeTableData[item]["需求"])
        //   upgrade_total["优化"] += parseInt(addedUpgradeTableData[item]["优化"])
        // }
        // // 将合计行放入addedUpgradeTableData中
        // addedUpgradeTableData.push(upgrade_total)

        // 对日常和增值两个表进行row 和 col的交换
        for (const item of dailyUpgradeTableData) {
          this.saasUpgradeData[0][0][item["resourcepool"]] = item['缺陷']
          this.saasUpgradeData[0][1][item["resourcepool"]] = item['需求']
          this.saasUpgradeData[0][2][item["resourcepool"]] = item['优化']
          this.saasUpgradeData[0][3][item["resourcepool"]] = item['升级次数']
        }

        for (const item of addedUpgradeTableData) {
          this.saasUpgradeData[1][0][item["resourcepool"]] = item['缺陷']
          this.saasUpgradeData[1][1][item["resourcepool"]] = item['需求']
          this.saasUpgradeData[1][2][item["resourcepool"]] = item['优化']
          this.saasUpgradeData[1][3][item["resourcepool"]] = item['升级次数']
        }

      } catch (error) {
        console.log(error)
        this.$message.error('错了哦，仔细看错误信息弹窗')
        alert('失败' + error)
      }

      //成功的消息提示
      this.$message({
        message:
          searchValue['beginData'] +
          ' 到 ' +
          searchValue['endData'] +
          ' 查询成功',
        type: 'success',
      })

      //■请求get完成后，就将参数赋到setOption中，如果放到get外面则无效了 调整各个图形的对应参数
      //受理情况的柱形图 复制修改它的 xAxis 和 series
      let myChart = echarts.getInstanceByDom(document.getElementById('myChart')) // 获取到当前的myChart实例
      // console.log('this.analysisData的myChart_xAxis',this.analysisData['myChart_xAxis']);
      // 计算柱形图的数据总和
      let total = 0
      for (var i = 0; i < this.analysisData['myChart_series'].length; i++) {
        total += parseInt(this.analysisData['myChart_series'][i])
      }

      console.log('总和', this.analysisData['myChart_series'])

      // 构造柱形图的 series 数据
      let seriesData = this.analysisData['myChart_series'].map(function (value) {
        let percentage = ((value / total) * 100).toFixed(2) // 计算百分比
        //弹出提示
        console.log('数值', value, total)
        return {
          value: value,
          label: {
            // 设置柱形图的数值
            show: true,
            position: 'top',
            align: 'center',
            // formatter: '{b|{b}}\n{c}次\n({d}%)'.replace('{d}', percentage),
            formatter: '{c|{c}}次\n({d|{d}%})'.replace('{d}', percentage),
            rich: {
              c: {
                color: '#4C5058',
                fontSize: 14,
              },
              d: {
                color: 'red',
                fontSize: 14,
                // fontWeight: 'bold',
              }
            }

          },
        }
      })

      // 使用构造好的 seriesData 绘制柱形图
      if (myChart) {
        // 修改xAxis的data参数
        myChart.setOption({
          xAxis: { data: this.analysisData['myChart_xAxis'] },
          // series: {data: this.analysisData['myChart_series']}
          series: { data: seriesData },
        })
      } //结束if判断

      // 嵌套环形图的数据放入
      let problemDict = {
        "softversion": "版本号",
        "total": "受理合计",
        "report": "报表功能",
        "openbill": "开票功能",
        "licenseReset": "license重置",
        "added": "增值服务",
        "collection": "收缴业务",
        "exchange": "通知交互",
        "writeoff": "核销功能",
        "billManagement": "票据管理",
        "security": "安全漏洞",
        "print": "打印功能",
        "datasync": "数据同步",
        "inverse": "反算功能",
        "opening": "单位开通",
        "softbug": "缺陷合计",
        "sspz": "实施配置",
        "ycsjcl": "异常数据处理"
      }

      let summaryRow = this.analysisData['tableData'].length - 1
      let summaryData = []
      for (let key in this.analysisData['tableData'][summaryRow]) {
        summaryData.push({ value: this.analysisData['tableData'][summaryRow][key], name: problemDict[key] })
      }
      let saasProblemPieChart = echarts.getInstanceByDom(
        document.getElementById('saasProblemPieChart')
      )
      if (saasProblemPieChart) {
        saasProblemPieChart.setOption({
          series: [
            {
              data: summaryData.slice(summaryData.length - 3, summaryData.length)
            },
            {
              data: summaryData.slice(2, summaryData.length - 3)
            }
          ]
        })
      }

    },
    // 结束 查询 事件

    exportAnalysePage(){
      const content = document.getElementById('news')
      html2pdf(
        content,
        {
          margin: 10,
          filename: 'saas数据汇报.pdf',
          image: { type: 'jpeg', quality: 0.98 },
          html2canvas: { scale: 5 },
          jsPDf: { unit: 'pt', format: 'a4', orientation: 'portrait' },
        }
      );
    },

    exportAnalysePage_1(){
      const content = document.getElementById('news')
      content.style.transform = 'scale(0.5)'
      const option = {
        margin: 10,
        scale: 0.45,
        image: { type: 'jpeg', quality: 0.98 },
        jsPDf: { unit: 'pt', format: 'a4', orientation: 'portrait' },
      }
      html2pdf(content, option).then((pdf)=> {
        pdf.save("saas数据汇报.pdf")
      })
      .catch((error) => {
        console.log("error generating pdf: ", error);
      });
    },

    // exportAnalysisPageToPDF(){
    //   const doc = new PDFDocument();
    //   const stream = doc.pipe(fs.createWriteStream('saas数据汇报.pdf'));
    //   doc.fontSize(25).text(document.documentElement.outerHTML, 50, 50);
    //   doc.end();
    //   stream.on('finish', function () {
    //     const link = document.createElement('a');
    //     liink.href = stream.toBlobURL('application/pdf');
    //     link.download = 'saas数据汇报.pdf';
    //     link.click();
    //   });
    // }
  },
}
</script>

<style scoped lang="scss">
::v-deep .el-table .el-table__footer-wrapper {
  background-color: rebeccapurple;
}
</style>

<style>

#saasProblemCharts {
  margin: 15px 0; 
  display: block
}
 
/* 通过设置div class对应的float方向，可以让两个div在同一行 */
.saasAnalysisTitle {
  color: #3398DB;
  font-size: 18;
  margin: 5px 10px 5px 0;
}

.myChart {
  float: left;
}

.saasProblemPieChart {
  float: left;
}

.clearFloat {
  clear: both;
}

.dailyUpgradeTable {
  width: 50%;
  display: inline-block;
  margin: 0 10px 0 0;
}

.addedUpgradeTable {
  width: 45%;
  display: inline-block;
  margin: 0 0 0 10px;
  float: right;
}
</style>

