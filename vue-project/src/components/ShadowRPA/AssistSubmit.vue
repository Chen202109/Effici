<template>
  <div class="component-wrapper">
    <search v-on:search="onSearch" ref="searchFilter"></search>

    <!-- 让新增记录的页面进行弹窗式的页面 :visible.sync是来控制dialog显示的属性，v-if是因为打开dialog之后会有上次的数据的缓存，使用v-if可以清空内存来清除之前的数据 -->
    <el-dialog :title=this.recordDetailInfoFormTitle :visible.sync="showRecordDetail" v-if="showRecordDetail" :close-on-click-modal="false">
      <add-form v-on:submit="onSubmit" ref="recordDetailInfoForm"></add-form>
    </el-dialog>

    <el-dialog title="批量新增" :visible.sync="showGroupAdd" v-if="showGroupAdd" :close-on-click-modal="false">
      <el-form style="text-align: center;">
        <el-form-item>
          <Upload ref="groupAddWorkRecord" :fileType="fileType" :fileLimitSize="fileLimitSize" :url="uploadUri" :fileLimit="fileLimitAmount" @closeUploadDialog="closeUploadDialog"></Upload>
        </el-form-item>
        <el-form-item>
          <el-button size=“medium” type="primary" @click="submitGroupAddWorkRecord">确认</el-button>
          <el-button size=“medium” @click="cancelGroupAddWorkRecord">取消</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>

    <el-button v-if="!showRecordDetail" type="primary" class="add-button" icon="el-icon-plus" @click="showRecordDetailForm('add', -1)">新增受理信息</el-button>
    <el-button v-if="!showGroupAdd" type="primary" class="add-button" icon="el-icon-plus" @click="showGroupAddDialog">批量新增</el-button>


    <ReportTable :table-data="workRecordTableData" v-on:handleSingleRecordOperation="onHandleSingleRecordOperation">
    </ReportTable>

    <!-- element-ui的分页组件 -->
    <el-pagination @size-change="handleSizeChange" @current-change="handleCurrentChange" :current-page.sync="currentPage"
      :page-sizes="pageSizes" :page-size.sync="currentPageSize" background layout="sizes, prev, pager, next"
      :total="workRecordTotalAmount">
    </el-pagination>
  </div>
</template>

<script>
import search from '@/components/ShadowRPA/AssistSubmit_search.vue'
import addForm from '@/components/ShadowRPA/AssistSubmit_addForm.vue'
import ReportTable from '@/components/ShadowRPA/AssistSubmit_table.vue'
import Upload from '@/components/Form/upload.vue'


export default {
  components: {
    search,
    addForm,
    ReportTable,
    Upload
  },
  data() {
    return {
      // 控制新增记录对话框的显示与隐藏
      showRecordDetail: false,
      showGroupAdd : false,

      // 上传文件的控制
      fileType  : ["xlsx", "csv", "xls", "xml"],
      fileLimitSize: 3,
      fileLimitAmount : 2,
      uploadUri : '/api/CMC/workrecords/work_record_group_add',

      // 记录详情表单的数据
      recordDetailInfoFormTitle: "",
      recordDetailInfoFormTitleOptions: { "add": "新增记录", "view": "查看详情", "edit": "编辑记录", "": "" },
      workRecordTableData: [],

      // 当前正在操作的行
      currentRow: -1,

      // 分页组件的数据
      pageSizes: [10, 20, 30, 50],
      currentPageSize: 10,
      currentPage: 1,
      workRecordTotalAmount: 1,

    }
  },
  mounted() {
    this.searchBasicInfo();
  },

  methods: {
    /**
     * 最开始页面加载的时候，默认查询前10条数据显示在表格上
     */
    searchBasicInfo() {
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
        if (filter["requestTotal"]) {
          this.currentPage = 1;
          //成功的消息提示
          this.$message({
            message: filter['beginData'] + ' 到 ' + filter['endData'] + ' 查询成功',
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
    onSubmit(operation, form) {
      console.log("tthhis form : ", operation, form)

      // 如果是查看详情
      if (operation === "view") {
        this.showRecordDetail = false;
      } else if (operation === "add") {
        // 新增工单记录
        this.$http.post(
          '/api/CMC/workrecords/work_record',
          form
        ).then(response => {
          this.showRecordDetail = false
          this.$message({
            message: '添加成功',
            type: 'success'
          })
          // 将total数量加一，并且进行一次查询更新展示的数据
          this.workRecordTotalAmount += 1;
          this.$refs.searchFilter.search(false);
        }).catch((error) => {
          console.log(error)
          this.$message.error('错了哦，仔细看错误信息弹窗')
          alert('失败' + error)
        })
      } else {
        // 修改工单记录
        this.$http.post(
          '/api/CMC/workrecords/work_record_update',
          form
        ).then(response => {
          this.showRecordDetail = false
          this.$message.success('修改成功')
          this.workRecordTableData[this.currentRow] = form
          this.currentRow = -1
        }).catch((error) => {
          console.log(error)
          this.$message.error('错了哦，仔细看错误信息弹窗')
          alert('失败' + error)
        })
      }
    },

    /**
     * 子组件的table里面的每行的查看修改删除操作的触发
     * @param {*} operation view, edit, delete
     * @param {*} recordInfoData 
     */
    onHandleSingleRecordOperation(operation, recordInfoData, rowIndex) {
      console.log("父组件: ", operation, recordInfoData);
      if (operation === "delete") {
        // 删除工单记录
        this.$http.post(
          '/api/CMC/workrecords/work_record_delete',
          recordInfoData
        ).then(response => {
          this.$message.success('删除成功')
          // 将total数量减一，并且进行一次查询更新展示的数据
          this.workRecordTotalAmount -= 1;
          this.$refs.searchFilter.search(false);
        }).catch((error) => {
          console.log(error)
          this.$message.error('错了哦，仔细看错误信息弹窗')
          alert('失败' + error)
        })
      } else {
        if (operation === "edit") this.currentRow = rowIndex;
        this.showRecordDetailForm(operation, recordInfoData)
      }
    },

    /**
     * 当进行新增，或者查看，或者编辑的时候，弹出具体信息的form框
     * @param {*} operation 有三种，新增 add，查看 view，编辑 edit
     * @param {*} id 如果是查看或者编辑的是有具体的编号，那么对应的id
     */
    showRecordDetailForm(operation, recordInfoData) {
      this.showRecordDetail = true
      this.recordDetailInfoFormTitle = this.recordDetailInfoFormTitleOptions[operation]
      this.$nextTick(() => {
        this.$refs.recordDetailInfoForm.initForm(operation, recordInfoData)  // init（）是子组件函数
      })
    },

    showGroupAddDialog(){
      this.showGroupAdd = true;
    },

    closeUploadDialog(){
      this.showGroupAdd = false;
    },

    /**
     * 进行批量新增操作，调用子组件的方法将文件进行上传检验，如果成功则关闭这个弹窗
     */
    submitGroupAddWorkRecord(){
      this.$refs.groupAddWorkRecord.submitFiles();
    },

    cancelGroupAddWorkRecord(){
      this.closeUploadDialog()
    },

    /**
     * 当点击更换当前页面的page显示多少条数据
     * @param {*} val 
     */
    handleSizeChange(val) {
      this.currentPage = 1
      // 触发子组件的search函数，那样就等于点击了一遍搜索那边的查询按钮进行请求
      this.$refs.searchFilter.search(false);

      // 切换展示条目数时滚动到容器顶部
      var that = this
      this.$nextTick(() => { that.scrollToTop(); })
    },

    /**
     * 当点击更换当前页面的page，切换分页
     * @param {*} val 
     */
    handleCurrentChange(val) {
      // 触发子组件的search函数，那样就等于点击了一遍搜索那边的查询按钮进行请求
      this.$refs.searchFilter.search(false);

      // 切换展示条目数时滚动到容器顶部
      var that = this
      this.$nextTick(() => { that.scrollToTop(); })
    },

    // 滚动到容器顶部
    scrollToTop() {
      const container = document.getElementById('AssistSubmit'); // 替换成你的容器ID
      if (container) {
        container.scrollTop = 0;
      }
    },

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

.el-pagination {
  margin-top: 20px;
}
</style>