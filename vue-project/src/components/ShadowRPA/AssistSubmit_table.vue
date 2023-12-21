<template>
  <div class="report-table">
    <el-table 
      :data="tableData"
      :header-cell-style="{ fontSize: '14px', color: '#696969', }"
      border 
      style="width: 100%" 
      highlight-current-row: true
    >
      <el-table-column label="操作" align="center" fixed="right">
        <!-- <el-col>
          <el-row style="margin: 5px 0;">
            <el-button size="mini" @click="handleDetail(scope.$index, scope.row)">详情</el-button>
          </el-row>
          <el-row style="margin: 5px 0;">
            <el-button size="mini" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
          </el-row>
          <el-row style="margin: 5px 0;">
            <el-button size="mini" @click="handleDelete(scope.$index, scope.row)" type="danger">删除</el-button>
          </el-row>
        </el-col> -->

        <el-row>
          <el-col :span="8">
            <el-button size="mini" @click="handleDetail(scope.$index, scope.row)">详情</el-button>
          </el-col>
          <el-col :span="8">
            <el-button size="mini" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
          </el-col>
          <el-col :span="8">
            <el-button size="mini" @click="handleDelete(scope.$index, scope.row)" type="danger">删除</el-button>
          </el-col>
        </el-row>
      </el-table-column>

      <el-table-column type="index" label="序号" width="50px" align="center"></el-table-column>

      <el-table-column v-for="(item, index) in tableTitle" :key="index" :prop="item.prop" :label="item.label"
                :width="columnWidth(item.label, 'saasWorkRecordDetailTable')" align="center"> </el-table-column>
      <el-table-column label="问题归属" :width="100" align="center"></el-table-column>
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
      tableTitle: [
        { prop: 'issolve', label: '解决' },
        { prop: 'createtime', label: '登记日期' },
        { prop: 'agenname', label: '单位名称' },
        { prop: 'region', label: '省份地区' },
        { prop: 'agentype', label: '产品类型' },
        { prop: 'environment', label: '环境属性' },
        { prop: 'errorfunction', label: '出错功能' },
        { prop: 'errortype', label: '问题分类' },
        { prop: 'softversion', label: '程序版本' },
        { prop: 'databasetype', label: '数据库类型' },
      ],
    };
  },
  methods: {

    /**
     * 计算el-table列的宽度
     */
    columnWidth(key, tableName) {
      let widthDict = {
        2: 57,
        3: 70,
        4: 78,
        5: 85,
        6: 110,
        10: 130,
      }
      let width
      if (tableName === 'saasWorkRecordDetailTable') {
        switch (key) {
          case '登记日期':
            width = 100
            break
          case '单位名称':
            width = 110
            break
          case '出错功能':
            width = 100
            break
          case '问题分类':
            width = 110
            break
          case '接入方':
            width = 80
            break
          case '数据库类型':
            width = 100
            break
          default:
            width = widthDict[key.length]
            break
        }
      } else if (key.length in widthDict){
        width = widthDict[key.length]
      }
      return width
    },


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
