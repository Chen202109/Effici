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
          <el-button type="primary" @click="search">查询</el-button>
        </div>
      </template>
    </div>

    <div style="margin: 15px 0">
      <template>
        <!-- 周末要发的受理信息数据-->
        <saasProblemTable :saasProblemTableData="this.tableData"></saasProblemTable>
      </template>
    </div>

    <div style="height: 30px;"></div>

    <div>
      <span class="saasAnalysisTitle"> SaaS各版本处理汇总</span>
      <el-select v-model="partySelected" placeholder="请选择" style="width: 110px;">
        <el-option v-for="(item, index) in this.partyList" :key="index" :label="item" :value="item"></el-option>
      </el-select>
    </div>
    <div style="margin: 15px 20px 15px 0;">
      <el-table :data="saasProblemTypeInVersions"
        :header-cell-style="{ fontSize: '14px', background: 'rgb(64 158 255 / 65%)', color: '#696969', }"
        :row-style="{ height: '25px' }" :cell-style="saasProblemTypeInVersionTableCellStyle" border style="width: 100%">
        <el-table-column v-for="(value, key) in saasProblemTypeInVersions[0]" :key="key" :prop="key"
          :label="key.replace(/\_/g, '.')" :width="columnWidth(key, 'saasProblemTypeInVersions')" align="center">
        </el-table-column>
      </el-table>

    </div>

  </div>
</template>

<script>
import { getMainPageWidth } from '@/utils/layoutUtil'
import saasProblemTable from '@/components/ShadowRPA/AnalysisData/AnalysisDataProblemTable.vue'

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
    * 进行 查询 事件,因为axios是异步的请求，所以会先处理数据，空闲了才处理异步数据
    */
    async search() {
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

      this.searchProblemTableData(searchValue)
      // this.searchSaasProblemTypeInVersions(searchValue)

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
          console.log('update local tableData data: ', response.data.data)
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
        if (response.data.status == 200) {
          // this.saasProblemTypeInVersions = response.data.data
          console.log('update local saasProblemTypeInVersions data: ', response.data.data)
        }else{
          console.log(response.message)
          this.$message.error(response.message)
        }
      }).catch((error) => {
        console.log(error)
        this.$message.error('错了哦，仔细看错误信息弹窗')
        alert('失败' + error)
      })
    }


  },
}
</script>