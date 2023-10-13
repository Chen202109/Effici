<template>
  <div class="report-table">
    <el-table :data="tableData" border style="width: 100%" highlight-current-row: true>
      <el-table-column type="expand" label="详情" width="50px">
        <template slot-scope="sprop">
          <el-form label-position="left" inline class="demo-table-expand">
            <el-form-item label="解决方案: ">
              <span style="color: blue;font-size:16px">{{ sprop.row.solveway }}</span>
            </el-form-item>
            <el-form-item label="原因分析: ">
              <span style="color: red;font-size:16px">{{ sprop.row.reason }}</span>
            </el-form-item>
          </el-form>
        </template>
      </el-table-column>
      <el-table-column type="index" label="序号" width="50px"></el-table-column>
      <el-table-column label="操作" width="150" align="center" fixed="left">
        <template slot-scope="scope">
          <el-button size="mini" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
          <el-button size="mini" type="danger" @click="handleDelete(scope.$index, scope.row)">删除</el-button>
        </template>
      </el-table-column>
      <el-table-column prop="issolve" label="解决" width="50px"></el-table-column>
      <el-table-column prop="agentype" label="产品类型" width="80px" align="center"></el-table-column>
      <el-table-column prop="environment" label="环境属性" width="80px" align="center"></el-table-column>
      <el-table-column prop="createtime" label="登记日期" width="100px" align="center"></el-table-column>
      <el-table-column prop="errortype" label="问题分类" width="80px" align="center"></el-table-column>
      <el-table-column prop="errorfunction" label="出错功能" width="80px" align="center"></el-table-column>
      <el-table-column prop="softversion" label="程序版本号" width="100px"></el-table-column>
      <el-table-column prop="problem" label="问题描述"></el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  name: "ReportTable",
  props: {
    tableData: {
      type: Array,
      default() {
        return [];
      },
    },
  },
  data() {
    return {
      showForm: false,
      // 这里的tableData 优先级低于 AssistSubmit.vue 处的，因为addForm和search组件可以将数据传给父组件，所以不能在这边填数据
      // tableData: [
      //   {
      // index: 1,
      //     issolve: '否',
      //     eventtype: '日常运维',
      //     createtime: '2023-7-3',
      //     endtime: '2023-7-3',
      //     region: '广西',
      //     softversion: 'V4.3.1.2',
      //     problem: "【单位】广西壮族自治区亭凉医院核销出错",
      //   },
      // ]
    };
  },
  methods: {
    handleEdit(index, row) {
      console.log("编辑", index, row.createtime);
    },
    handleDelete(index, row) {
      console.log("删除", index, row);
    },
  },
};
</script>
<style scoped>
.demo-table-expand {
  font-size: 0;
}
.demo-table-expand label {
  width: 90px;
  color: #99a9bf;
}
.demo-table-expand .el-form-item {
  margin-right: 0;
  margin-bottom: 0;
  width: 50%;
}
/* .report-table {

} */
</style>
