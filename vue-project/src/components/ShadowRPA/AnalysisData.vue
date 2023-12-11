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
      <div class="myChart" id="myChart" :style="{ width: getPageWidth * 0.5 + 'px', height: '420px' }"></div>
      <div class="saasProblemPieChart" id="saasProblemPieChart" :style="{ width: getPageWidth * 0.5 + 'px', height: '420px' }"></div>
    </div>

    <div class="clearFloat"></div>

    <div style="height: 30px;"></div>

    <p class="saasAnalysisTitle"> SaaS各版本处理汇总</p>
    <div style="margin: 15px 20px 15px 0;">
      <el-table :data="saasProblemTypeInVersions"
        :header-cell-style="{ fontSize: '14px', background: 'rgb(64 158 255 / 65%)', color: '#696969', }"
        :row-style="{ height: '25px' }" :cell-style="saasProblemTypeInVersionTableCellStyle" border style="width: 100%">
        <el-table-column v-for="(value, key) in saasProblemTypeInVersions[0]" :key="key" :prop="key"
          :label="key.replace(/\_/g, '.')" :width="columnWidth(key, 'saasProblemTypeInVersions')" align="center">
        </el-table-column>
      </el-table>

      <el-table v-for="(item, index) in saasProblemTypeInVersionsDetail" :key="index" :data="item"
        :header-cell-style="{ fontSize: '14px', background: 'rgb(64 158 255 / 65%)', color: '#696969', }"
        :row-style="{ height: '25px' }" :cell-style="saasProblemTypeInVersionTableCellStyle" border style="width: 100%; margin: 15px 20px 15px 0;">
        <el-table-column v-for="(value, key) in item[0]" :key="key" :prop="key"
          :label="key.replace(/\_/g, '.')" :width="columnWidth(key, 'saasProblemTypeInVersions')" align="center">
        </el-table-column>
      </el-table>
    </div>

  </div>
</template>

<script>
import { getMainPageWidth } from '@/utils/layoutUtil'
import saasProblemTable from '@/components/ShadowRPA/AnalysisData_saasProblemTable.vue'
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
    saasProblemTable
  },
  data() {
    return {
      // saasProblemTableData这个总表格的表头
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
      //查询日期
      dateRange: [new Date(new Date().getFullYear() + '-' + (new Date().getMonth() + 1) + '-01'),new Date()],
      // 出错功能的key的对照，因为后台返回的数据的key是缩写，所以需要一个对照
      problemDict : {
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
      },
      // SaaS各版本处理汇总的表格数据
      saasProblemTypeInVersions: [],
      // SaaS各版本 产品bug, 实施配置，异常数据处理 汇总的表格数据
      saasProblemTypeInVersionsDetail: [ [], [], [] ],
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
      },

    }
  },
  // 计算页面刚加载时候渲染的属性
  computed: {
    getPageWidth: getMainPageWidth
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
        xAxis: {
          axisLabel: { interval: 0 },
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
          top: '15%',
          bottom: '10%',
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
            data: []
          },
          {
            name: 'Access From',
            type: 'pie',
            // 设定外圈的环的大小
            radius: ['48%', '62%'],
            top: "1%",
            left: 'center',
            // width不直接指定，因为这个图的大小是通过整个屏幕计算宽度除以2得到的，所以和这个图的宽度保持一直，具体算法见util中的layoutUtil的getMainPageWidth()方法
            width: (window.screen.width - 20 * 2 - 220 - 10 * 2 - 1 * 2 - 15 * 2 - 20 - 15)/2,
            labelLine: {
              length: 15,
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
                },
              }
            },
            // 给标签线设置格式
            labelLayout: function (params) {
              // 通过标签魔性labelRect的x，查看是在这张图左边还是右边 （不能使用params.label.x直接看label的文字的坐标，不知道为什么直接整个回调所有设置失效）
              const isLeft = params.labelRect.x < saasProblemPieChart.getWidth() / 2;
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
            data: []
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

    /**
     * 计算el-table列的宽度
     */
    columnWidth(key, tableName) {
      // 因为当标题是版本号比如V4.3.2.0的时候，表头会显示不完全，所以在生成表格column的时候将版本之中的.给给成了_,如果这时候要计算想要的宽度，就把它给改回来
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
      if (tableName === 'saasProblemTypeInVersions' && (["问题分类" , "产品bug" , "实施配置" , "异常数据处理"].includes(key))) {
        width = 110 
      } else if (key.length in widthDict){
        width = widthDict[key.length]
      }
      return width
    },

    /**
     * 在查询之后更新版本的数据信息
     */
    updateSaasProblemTypeInVersions(){
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
    },

    /**
     * 查询之后，将更新的数据放入SaaS各版本受理汇总的柱状图中然后渲染
     */
    updateMyChart(){
      //受理情况的柱形图 复制修改它的 xAxis 和 series
      let myChart = echarts.getInstanceByDom(document.getElementById('myChart')) // 获取到当前的myChart实例
      // 计算柱形图的数据总和
      let total = 0
      for (var i = 0; i < this.analysisData['myChart_series'].length; i++) {
        total += parseInt(this.analysisData['myChart_series'][i])
      }

      // 构造柱形图的 series 数据
      let seriesData = this.analysisData['myChart_series'].map(function (value) {
        let percentage = ((value / total) * 100).toFixed(2) // 计算百分比
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

      let xAxisData = this.analysisData['myChart_xAxis'].map((item, index) => (index%2===0)?item: '\n'+item)
      xAxisData =(this.analysisData['myChart_xAxis'].length > 8)? xAxisData: this.analysisData['myChart_xAxis']
      // 使用构造好的 seriesData 绘制柱形图
      // 修改xAxis的data参数
      myChart && myChart.setOption({
          xAxis: { data: xAxisData},
          series: { data: seriesData },
      })

    },

    /**
     * 查询之后，将更新的数据放入嵌套环形图中然后渲染
     */
    updateSaasProblemPieChart(){
      // 嵌套环形图的数据放入
      let summaryRow = this.analysisData['tableData'].length - 1
      let summaryData = []
      for (let key in this.analysisData['tableData'][summaryRow]) {
        summaryData.push({ value: this.analysisData['tableData'][summaryRow][key], name: this.problemDict[key] })
      }
      let saasProblemPieChart = echarts.getInstanceByDom(document.getElementById('saasProblemPieChart'))
      saasProblemPieChart && saasProblemPieChart.setOption({
          series: [
            {
              data: summaryData.slice(summaryData.length - 3, summaryData.length)
            },
            {
              data: summaryData.slice(2, summaryData.length - 3)
            }
          ]
      })
    },

    /**
     * 查询指定时间内的工单记录的问题类别与出错功能的对比数据
     * @param {*} searchValue 
     */
    async searchSaasProblemTypeInVersions(searchValue){
      try {
        const response = await this.$http.get(
          '/api/CMC/workrecords/analysis_saas_problem_type_in_versions?beginData=' +
          searchValue['beginData'] +
          '&endData=' +
          searchValue['endData']
        )
        console.log(response.data.data)
        this.saasProblemTypeInVersionsDetail = [ [], [], [] ]
        for ( let i = 0; i < this.saasProblemTypeInVersionsDetail.length; i++) {
          this.saasProblemTypeInVersionsDetail[i] = response.data.data[i]['problemTypeData']
        }
      } catch (error) {
        console.log(error)
        this.$message.error('错了哦，仔细看错误信息弹窗')
        alert('失败' + error)
      }
    },

    /**
     * 进行 查询 事件,因为axios是异步的请求，所以会先处理数据，空闲了才处理异步数据
     */
    async search() {
      // 触发查询事件，根据日期条件进行查询
      var searchValue = {} // 存放筛选条件信息
      // 获取年、月、日，进行拼接
      for (let i = 0; i < this.dateRange.length; i++) {
        var year = this.dateRange[i].getFullYear()
        var month = ('0' + (this.dateRange[i].getMonth() + 1)).slice(-2)
        var day = ('0' + this.dateRange[i].getDate()).slice(-2)
        searchValue[i == 0 ? 'beginData' : 'endData'] = year + '-' + month + '-' + day;
      } 

      // 使用axios发送请求 
      try {
        const response = await this.$http.get(
          '/api/CMC/workrecords/analysisselect?beginData=' +
          searchValue['beginData'] +
          '&endData=' +
          searchValue['endData']
        )
        console.log('获得 response data 为', response.data.data)
        this.analysisData = []
        this.analysisData = response.data.data // 这里不能将整个data赋过去，会造成其他数据被覆盖
        console.log('获得 this.analysisData 为', this.analysisData)

        this.updateSaasProblemTypeInVersions()

        //成功的消息提示
        this.$message({
          message: searchValue['beginData'] + ' 到 ' + searchValue['endData'] + ' 查询成功',
          type: 'success',
        })

      } catch (error) {
        console.log(error)
        this.$message.error('错了哦，仔细看错误信息弹窗')
        alert('失败' + error)
      }

      this.searchSaasProblemTypeInVersions(searchValue)

      //■请求get完成后，就将参数赋到setOption中，如果放到get外面则无效了 调整各个图形的对应参数
      this.updateMyChart()
      this.updateSaasProblemPieChart()
    },

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
</style>

