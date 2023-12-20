<template>
  <div class="component-wrapper">
    <search v-on:search="onSearch" ref="searchFilter"></search>
    <!-- 让新增记录的页面进行弹窗式的页面 :visible.sync是来控制dialog显示的属性，v-if是因为打开dialog之后会有上次的数据的缓存，使用v-if可以清空内存来清除之前的数据 -->
    <el-dialog title="新增记录" :visible.sync="showForm" v-if="showForm" :close-on-click-modal="false">
      <add-form v-on:submit="onSubmit"></add-form>
    </el-dialog>
    <el-button v-if="!showForm" type="primary" class="add-button" icon="el-icon-plus" @click="showForm = true">新增受理信息</el-button>
	  <ReportTable :table-data="workRecordTableData"></ReportTable>
    <!-- element-ui的分页组件 -->
    <el-pagination
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      :current-page.sync="currentPage"
      :page-sizes="pageSizes"
      :page-size.sync = "currentPageSize"
      background
      layout="sizes, prev, pager, next"
      :total="workRecordTotalAmount">
    </el-pagination>
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
      workRecordTableData: [],

      // 分页组件的数据
      pageSizes : [10, 20, 30, 50],
      currentPageSize: 10,
      currentPage: 1,
      workRecordTotalAmount : 500,
    }
  },
  mounted() {
    this.searchBasicInfo()
  },
  methods: {

    searchBasicInfo(){
      // 触发子组件的search函数，那样就等于点击了一遍搜索那边的查询按钮进行请求
      this.$refs.searchFilter.search(true);
    },

    /**
     * 搜索工单详细信息的记录
     * @param {*} filter 搜索的子组件中传递出来的筛选信息
     */
    onSearch(filter) {
      // 根据筛选条件筛选数据并渲染表格
      this.$http.get(
        '/api/CMC/workrecords/work_record?searchFilter=' + 
        JSON.stringify(filter) + 
        '&page=' + 
        this.currentPage +
        '&pageSize=' +
        this.currentPageSize
      ).then((response) => {
        // 更新表格数据和total的amount
        this.workRecordTableData = response.data.data;
        this.workRecordTotalAmount = (response.data.amount === -1) ? this.workRecordTotalAmount : response.data.amount;
        // 如果是搜索的情况而不是翻页的情况，将当前页面重置回1，然后消息提示查询成功
        if (filter["requestTotal"]){
          this.currentPage = 1;
          //成功的消息提示
          this.$message({
            message: filter['beginData']+' 到 '+filter['endData']+' 查询成功',
            type: 'success'
          });
        }
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
    },

    handleSizeChange(val) {
      console.log(`每页 ${val} 条`);
      this.currentPage = 1
      // 触发子组件的search函数，那样就等于点击了一遍搜索那边的查询按钮进行请求
      this.$refs.searchFilter.search(false);
    },
    handleCurrentChange(val) {
      console.log(`当前页: ${val}`);
      // 触发子组件的search函数，那样就等于点击了一遍搜索那边的查询按钮进行请求
      this.$refs.searchFilter.search(false);
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