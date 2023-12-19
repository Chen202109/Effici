<template>
  <div class="component-wrapper">
    <search v-on:search="onSearch"></search>
    <!-- 让新增记录的页面进行弹窗式的页面 :visible.sync是来控制dialog显示的属性，v-if是因为打开dialog之后会有上次的数据的缓存，使用v-if可以清空内存来清除之前的数据 -->
    <el-dialog title="新增记录" :visible.sync="showForm" v-if="showForm" :close-on-click-modal="false">
      <add-form v-on:submit="onSubmit"></add-form>
    </el-dialog>
    <el-button v-if="!showForm" type="primary" class="add-button" icon="el-icon-plus" @click="showForm = true">新增受理信息</el-button>
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
      tableData: []
    }
  },
    methods: {

      /**
       * 搜索工单详细信息的记录
       * @param {*} filter 
       */
      onSearch(filter) {
        // 根据筛选条件筛选数据并渲染表格
        this.$http.get(
          '/api/CMC/workrecords/work_record?searchFilter='+JSON.stringify(filter)
        ).then((response) => {
          console.log("work record detail search result: ", response.data.data);
          this.tableData = response.data.data;
          //成功的消息提示
          this.$message({
            message: filter['beginData']+' 到 '+filter['endData']+' 查询成功',
            type: 'success'
          });
        }).catch(function (error) {
          console.log(error);
          this.$message.error('错了哦，仔细看错误信息弹窗');
          alert("失败" + error);
        });
      },

      /**
       * 提交新增/修改工单数据的表单给后端，将更改的内容存储到数据库
       * @param {*} form 
       */
      onSubmit(form) {
        console.log("tthhis form : ", form)
        this.$http.post(
          '/api/CMC/workrecords/work_record', 
          form
        ).then(response => {
          console.log("dddd, this response: ", response)
          this.showForm = false
          this.$message({
            message: '添加成功',
            type: 'success'
          })
        }).catch((error)=>{
        console.log(error)
          this.$message.error('错了哦，仔细看错误信息弹窗')
          alert('失败' + error)
        })
      }
  }
}
</script>

<style scoped>
.component-wrapper {
  padding: 20px;
}
.add-button {
  margin-bottom: 20px;
}
</style>