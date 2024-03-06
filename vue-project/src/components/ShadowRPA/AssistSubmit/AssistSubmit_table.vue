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

        <template slot-scope="scope">
          <el-row>
            <el-col :span="8">
              <el-button size="mini" @click="handleSingleRecordOperation('view', scope.row)">详情</el-button>
            </el-col>
            <el-col :span="8">
              <el-button size="mini" @click="handleSingleRecordOperation('edit', scope.row, scope.$index)">编辑</el-button>
            </el-col>
            <el-col :span="8">
              <el-button size="mini" @click="handleSingleRecordOperation('delete', scope.row)" type="danger">删除</el-button>
            </el-col>
          </el-row>
        </template>
      </el-table-column>

      <el-table-column type="index" label="序号" width="50px" align="center"></el-table-column>

      <el-table-column v-for="(item, index) in tableTitle" :key="index" :prop="item.prop" :label="item.label"
                :width="myColumnWidth(item.label, 'saasWorkRecordDetailTable')" align="center"> </el-table-column>
    </el-table>
  </div>
</template>

<script>
import { columnWidth } from '@/utils/layoutUtil'
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
        { prop: 'isSolved', label: '解决' },
        { prop: 'registerDate', label: '登记日期' },
        { prop: 'agencyName', label: '单位名称' },
        { prop: 'province', label: '省份地区' },
        { prop: 'productType', label: '产品类型' },
        { prop: 'deployment', label: '环境属性' },
        { prop: 'errorFunction', label: '出错功能' },
        { prop: 'problemType', label: '问题分类' },
        { prop: 'version', label: '程序版本' },
        { prop: 'DBType', label: '数据库类型' },
        { prop: 'problemAttribution', label: '问题归属' },
      ],
    };
  },
  methods: {

    /**
     * 计算el-table列的宽度
     */
    myColumnWidth(key, tableName) {

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
            width = columnWidth(key)
            break
        }
      } else{
        width = columnWidth(key)
      }
      return width === undefined ? 100 : width
    },

    handleSingleRecordOperation(operation, recordInfoData, rowIndex) {
      console.log("子组件", operation, recordInfoData, rowIndex);
      // 避免修改原来的值，进行浅拷贝
      var recordInfoDataCopy = Object.assign({}, recordInfoData);
      // 因为如果是要打开form，form里将problemAttribution分成了可以选择的两个下拉框，所以这里需要将problemAttribution进行拆分
      if (recordInfoDataCopy.problemAttribution == "" || recordInfoDataCopy.problemAttribution == null){
        recordInfoDataCopy["problemParty"] = ""
        recordInfoDataCopy["problemAttribution"] = ""
      }else {
        recordInfoDataCopy["problemParty"] = recordInfoDataCopy.problemAttribution.split("-")[0];
        recordInfoDataCopy["problemAttribution"] = recordInfoDataCopy.problemAttribution.split("-")[1];
      }
      this.$emit("handleSingleRecordOperation", operation, recordInfoDataCopy, rowIndex);
    },
    
  },
};
</script>
<style scoped>

</style>
