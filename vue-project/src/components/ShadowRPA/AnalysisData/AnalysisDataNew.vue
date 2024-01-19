<template>
  <!-- 所有的内容要被根节点包含起来-->
  <div>
    <div style="margin: 15px 0">
      <template>
        <div class="block">
          <span class="demonstration">分析范围： </span>
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期"
            end-placeholder="结束日期">
          </el-date-picker>
          <el-button type="primary" @click="search(1)">查询</el-button>
        </div>
      </template>
    </div>

    <div style="margin: 15px 0">
      <template>
        <!-- 周末要发的受理信息数据-->
        <saasProblemTable :saasProblemTableData="this.tableData"></saasProblemTable>
      </template>
    </div>

    <div class='saasProblemCharts'>
      <!-- 放入Echarts 可视化图形 组件 -->
      <div class="saasProblemBarChartNew" id="saasProblemBarChartNew" :style="{ width: getPageWidth * 0.5 + 'px', height: '420px' }"></div>
      <div class="saasProblemPieChartNew" id="saasProblemPieChartNew" :style="{ width: getPageWidth * 0.5 + 'px', height: '420px' }"></div>
    </div>

    <div class="clearFloat"></div>

    <div style="height: 30px;"></div>

    <div>
      <span class="saasAnalysisTitle"> SaaS各版本处理汇总</span>
      <el-select v-model="partySelected" placeholder="请选择" style="width: 110px;">
        <el-option v-for="(item, index) in this.partyList" :key="index" :label="item" :value="item"></el-option>
      </el-select>
      <el-button type="primary" @click="search()">查询</el-button>
    </div>
    <div style="margin: 15px 20px 15px 0;">
      <!-- v-for里key多添加一个值是因为有时候会和其他v-for冲突在一起，这里的是有可能v-for这里寻找key去update的时候会update到下面的saasProblemTypeInVersionsDetail -->
      <el-table v-for="(item, index) in saasProblemTypeInVersions" :key="index+saasProblemTypeInVersions" :data="item"
        :header-cell-style="{ fontSize: '14px', background: 'rgb(64 158 255 / 65%)', color: '#696969', }"
        :row-style="{ height: '25px' }" :cell-style="saasProblemTypeInVersionTableCellStyle" border style="width: 100%; margin: 15px 20px 15px 0;">
        <el-table-column v-for="(value, key) in item[0]" :key="key" :prop="key"
          :label="key.replace(/\_/g, '.')" :width="columnWidth(key, 'saasProblemTypeInVersions')" align="center">
        </el-table-column>
      </el-table>

      <el-table v-for="(item, index) in saasProblemTypeInVersionsDetail" :key="index+saasProblemTypeInVersionsDetail" :data="item"
        :header-cell-style="{ fontSize: '14px', background: 'rgb(64 158 255 / 65%)', color: '#696969', }"
        :row-style="{ height: '25px' }" :cell-style="saasProblemTypeInVersionTableCellStyle" border style="width: 100%; margin: 15px 20px 15px 0;">
        <el-table-column v-for="(value, key) in item[0]" :key="key" :prop="key"
          :label="key.replace(/\_/g, '.')" :width="columnWidth(key, 'saasProblemTypeInVersions')" align="center">
        </el-table-column>
      </el-table>

      <el-table v-for="(item, index) in saasProblemTypeFunctionInVersions" :key="index+saasProblemTypeFunctionInVersions" :data="item"
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
import { updateBarChartBasic} from '@/utils/echartBasic'
import saasProblemTable from '@/components/ShadowRPA/AnalysisData/AnalysisDataProblemTable.vue'
// 引入基本模板
let echarts = require('echarts/lib/echarts')

export default {
  name: 'AnalysisData',
  components: {
    saasProblemTable
  },
  data() {
    return {
      //查询日期
      dateRange: [new Date(new Date().getFullYear() + '-' + (new Date().getMonth() + 1) + '-01'), new Date()],

      partyList: ["全部", "行业", "财政", "第三方"],
      partySelected: "全部",

      // SaaS各版本处理汇总的表格数据
      saasProblemTypeInVersions: [],
      saasProblemTypeInVersionsDetail : [],

      tableData: [{
        "程序版本": "合计",
        "受理合计": 0,
        "开票功能": 0,
        "收缴业务": 0,
        "核销功能": 0,
        "反算功能": 0,
        "通知交互": 0,
        "票据管理": 0,
        "数据同步": 0,
        "打印功能": 0,
        "基础信息": 0,
        "报表功能": 0,
        "安全漏洞": 0,
        "license重置": 0,
        "单位开通": 0,
        "增值服务": 0
      }],
    }
  },

  // 计算页面刚加载时候渲染的属性
  computed: {
    getPageWidth: getMainPageWidth
  },

  mounted() {
    this.drawLine()
  },

  methods: {

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
      if (tableName === 'saasProblemTypeInVersions') {
        if (["产品bug" , "实施配置" , "异常数据处理", "需求", "其他"].some(str => key.includes(str))){
          width = 200
        } else if (key.search("问题因素") !== -1){
          width = 150
        } else {
          width = widthDict[key.length]
        }
      } else {
        width = widthDict[key.length]
      }
      return width === undefined ? 100 : width
    },


    drawLine() {
      let saasProblemBarChartNew = echarts.init(document.getElementById('saasProblemBarChartNew'))
      let saasProblemPieChartNew = echarts.init(document.getElementById('saasProblemPieChartNew'))

      saasProblemBarChartNew.setOption({
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
      
      saasProblemPieChartNew.setOption({
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
              const isLeft = params.labelRect.x < saasProblemPieChartNew.getWidth() / 2;
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


   /**
    * 进行 查询 事件,因为axios是异步的请求，所以会先处理数据，空闲了才处理异步数据
    * @param {*} searchFlag 如果为1，则代表全局搜索，会将这个页面所有需要搜索的东西都搜索了。
    */
    async search(searchFlag) {
      // 触发查询事件，根据日期条件进行查询
      var searchValue = {} // 存放筛选条件信息
      searchValue["partySelected"] = this.partySelected
      // 获取年、月、日，进行拼接
      for (let i = 0; i < this.dateRange.length; i++) {
        var year = this.dateRange[i].getFullYear()
        var month = ('0' + (this.dateRange[i].getMonth() + 1)).slice(-2)
        var day = ('0' + this.dateRange[i].getDate()).slice(-2)
        searchValue[i == 0 ? 'beginData' : 'endData'] = year + '-' + month + '-' + day;
      }

      if (searchFlag === 1) this.searchProblemTableData(searchValue)
      this.searchSaasProblemTypeInVersions(searchValue)
      this.searchSaasProblemTypeDetailInVersions(searchValue)
      this.searchSaasProblemTypeFunctionInVersionsDetail(searchValue)

    },

    async searchProblemTableData(searchValue) {
      this.$http.get(
        '/api/CMC/workrecords/analysis_select_new?beginData=' +
        searchValue['beginData'] +
        '&endData=' +
        searchValue['endData'] 
      ).then(response => {
        if (response.data.status === 200) {
          this.tableData = response.data.data
          console.log('response data: ', response.data.data)
          console.log('update local tableData data: ', response.data.data)
          this.updateSaasProblemBarChart()
          this.updateSaasProblemPieChart()
          
        }else{
          console.log(response.message)
          this.$message.error(response.message)
        }
      }).catch((error) => {
        console.log("失败" + error)
        this.$message.error('错了哦，仔细看错误信息弹窗')
        alert('失败' + error)
      })
    },

    async searchSaasProblemTypeInVersions(searchValue) {
      this.$http.get(
        '/api/CMC/workrecords/analysis_saas_problem_type_in_versions_new?beginData=' +
        searchValue['beginData'] +
        '&endData=' +
        searchValue['endData'] +
        '&partySelected=' +
        searchValue['partySelected']
      ).then(response => {
        if (response.data.status === 200) {
          // 清空原来的数据
          this.saasProblemTypeInVersions = []
          for ( let i = 0; i < response.data.data.length; i++) {
            this.saasProblemTypeInVersions.push(response.data.data[i]['problemData'])
          }
          console.log('response data: ', response.data.data)
          console.log('update local saasProblemTypeInVersions data: ', this.saasProblemTypeInVersions)
        }else{
          console.log(response.message)
          this.$message.error(response.message)
        }
      }).catch((error) => {
        console.log("失败" + error)
        this.$message.error('错了哦，仔细看错误信息弹窗')
        alert('失败' + error)
      })
    },

    async searchSaasProblemTypeDetailInVersions(searchValue) {
      this.$http.get(
        '/api/CMC/workrecords/analysis_saas_problem_type_detail_in_versions_new?beginData=' +
        searchValue['beginData'] +
        '&endData=' +
        searchValue['endData'] +
        '&partySelected=' +
        searchValue['partySelected']
      ).then(response => {
        if (response.data.status == 200) {
          // 清空原来的数据
          this.saasProblemTypeInVersionsDetail = []
          for ( let i = 0; i < response.data.data.length; i++) {
            this.saasProblemTypeInVersionsDetail.push(response.data.data[i]['problemData'])
          }
        }else{
          console.log(response.message)
          this.$message.error(response.message)
        }
      }).catch((error) => {
        console.log(error)
        this.$message.error('错了哦，仔细看错误信息弹窗')
        alert('失败' + error)
      })
    },

    async searchSaasProblemTypeFunctionInVersionsDetail(searchValue) {
      this.$http.get(
        '/api/CMC/workrecords/analysis_saas_problem_type_in_function_version_view_new?beginData=' +
        searchValue['beginData'] +
        '&endData=' +
        searchValue['endData'] +
        '&partySelected=' +
        searchValue['partySelected']
      ).then(response => {
        if (response.data.status == 200) {
          this.saasProblemTypeFunctionInVersions = []
          for ( let i = 0; i < response.data.data.length; i++) {            
            this.saasProblemTypeFunctionInVersions.push(response.data.data[i]['problemData'])
          }
        }else{
          console.log(response.message)
          this.$message.error(response.message)
        }
      }).catch((error) => {
        console.log(error)
        this.$message.error('错了哦，仔细看错误信息弹窗')
        alert('失败' + error)
      })
    },

    updateSaasProblemBarChart(){
      var saasProblemBarChartNewData = [{"seriesName":"SaaS各版本受理汇总", "seriesData":[]}]
      var totalAmount = this.tableData[this.tableData.length-1]["受理合计"]
      for(var i = 0; i < this.tableData.length-1; i++){
        saasProblemBarChartNewData[0]["seriesData"].push({'x':this.tableData[i]["程序版本"], "y": this.tableData[i]["受理合计"], "percent":((this.tableData[i]["受理合计"] / totalAmount) * 100).toFixed(2)})
      }
      updateBarChartBasic(document, saasProblemBarChartNewData, 'SaaS各版本受理汇总', "category", false, true, 'saasProblemBarChartNew')
      let saasProblemBarChartNew = echarts.getInstanceByDom(document.getElementById("saasProblemBarChartNew"))
      saasProblemBarChartNew && saasProblemBarChartNew.setOption({
        series: {
          label : {
            show: true,
            formatter: function (params) {
              const index = params.dataIndex; // 当前数据点的索引
              const dataPoint = saasProblemBarChartNewData[0]["seriesData"][index]
              return '{c|{c}}次\n({d|{d}%})'.replace('{c}', dataPoint.y).replace('{d}', dataPoint.percent);
            },
            position: 'top',
            rich: {
              c: {
                color: '#4C5058',
                fontSize: 14,
              },
              d: {
                color: 'red',
                fontSize: 14,
              }
            }
          },
        },
      })
    },

    updateSaasProblemPieChart() {
      // 嵌套环形图的数据放入
      let summaryRow = this.tableData.length - 1
      let summaryData = []
      for (let key in this.tableData[summaryRow]) {
        summaryData.push({ value: this.tableData[summaryRow][key], name: key })
      }
      let saasProblemPieChartNew = echarts.getInstanceByDom(document.getElementById('saasProblemPieChartNew'))
      // 问题因素只展示最多的前三项
      var errorFactorData = summaryData.slice(summaryData.length - 5, summaryData.length)
      errorFactorData.sort((a, b) => b.value - a.value)
      errorFactorData = errorFactorData.slice(0,3)
      saasProblemPieChartNew && saasProblemPieChartNew.setOption({
          series: [
            { data:  errorFactorData},
            { data: summaryData.slice(2, summaryData.length - 5) }
          ]
      })
    }

  },
}
</script>

<style scoped>

.saasProblemCharts {
  margin: 15px 0; 
  display: block
}
.saasAnalysisTitle {
  color: #3398DB;
  font-size: 18;
  margin: 5px 10px 5px 0;
}

.saasProblemBarChartNew, .saasProblemPieChartNew {
  float: left;
}

.clearFloat {
  clear: both;
}
</style>