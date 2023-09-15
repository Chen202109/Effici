<template>
  <div class="component-wrapper">
    <search v-on:search="onSearch"></search>
    <add-form v-if="showForm" v-on:submit="onSubmit"></add-form>
    <el-button v-if="showForm != true" type="primary" class="add-button" icon="el-icon-plus" @click="showForm = true">新增受理信息</el-button>
	  <ReportTable :table-data="tableData"></ReportTable>
  </div>
</template>

<script>
import search from '@/components/ShadowRPA/AssistSubmit_search.vue'
import addForm from '@/components/ShadowRPA/AssistSubmit_addForm.vue'
import ReportTable from '@/components/ShadowRPA/AssistSubmit_table.vue'

export default {
  components: {
    search,
    addForm,
    ReportTable
  },
  data() {
    return {
	    showForm: false,
      tableData: [
        {
		      index: 1,
          issolve: '是',
          agentype: '医疗',
          environment: '私有化',
          createtime: '2023-07-03',
          errortype: '产品BUG',
          errorfunction: '开票功能',
          softversion: 'V4.3.1.2',
          problem: "【单位】广西壮族自治区亭凉医院\n[程序版本】4312\n【问题描述】审验申请提示未查询到日结任务进度信息，参数：tenantCode=0,regionCode=450000,agencyIdCode=3a0ef31528674588915d9b801575a19b,name=DailyUseMergeRecordJob",
          solveway: "une_ebill fremitPayState字段改为0",
          reason:"已汇缴。此BUG已经修复"
        },
      ]
    }
  },
    methods: {
    onSearch(filter) {
      // 根据筛选条件筛选数据并渲染表格
      // ...
      console.log('父组件接到了数据',filter)
      console.log('打印出父组件接收到的起始日期',filter['beginData'])
      this.$http.get("/api/CMC/workrecords/select?beginData="+filter['beginData']+"&endData="+filter['endData']+"&problem="+filter['problem']+"&errortype="+filter['errortype']).then((response) => {
        //this.templates= response.data.data;
        console.log(response.data.data);
        this.tableData = response.data.data;
        //成功的消息提示
        this.$message({
          message: filter['beginData']+' 到 '+filter['endData']+' 查询成功',
          type: 'success'
        });
      })
      .catch(function (error) {
        console.log(error);
        this.$message.error('错了哦，仔细看错误信息弹窗');
        alert("失败" + error);
      });
      //this.tableData = filteredData
    },
    onSubmit(form) {
      // 将表单数据保存到数据库
      // ...
      this.showForm = false
      this.$message({
        message: '添加成功',
        type: 'success'
      })
    }
  }
}
</script

<style scoped>
.component-wrapper {
  padding: 20px;
}
.add-button {
  margin-bottom: 20px;
}
</style>