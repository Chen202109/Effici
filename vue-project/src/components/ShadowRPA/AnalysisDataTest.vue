
<template>
    <div id="compositeLeftMiddle">

          <el-table
            :data="analysisData['tableData']" 
            :row-style="{ height: '30px' }" 
            :header-cell-style="{fontSize:'14px',background:'#DDDDDD',color:'#696969'}"
            style="width: 100%;font-size:10px;"
            :cell-style="cellStyle" >
            <el-table-column prop="softversion" label="程序版本" width="80" align="center" > </el-table-column>
            <el-table-column v-for="(item, index) in tableTitle" :key="index" :prop="item.prop" :label="item.label" width="78" align="center"> </el-table-column>
          </el-table>

    </div>
  </template>
  
  <script>
  export default {
    name: "LeftMiddle",
    data() {
      return {
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
        // upgradeData 升级计划表格的数据
        upgradeData: [
          { resourcepool: '01资源池', 缺陷: '0', 需求: '0', 优化: '0' },
        ], // 升级表格数据
        // licenseData license表格的数据
        licenseData: [
          {
            省份: '申请单位数',
            北京: 999,
            山西: 99,
            内蒙古: 99,
            辽宁: 99,
            吉林: 99,
            黑龙江: 99,
            上海: 99,
            安徽: 99,
            福建: 99,
            江西: 999,
            山东: 99,
            河南: 99,
            湖北: 99,
            广东: 99,
            广西: 99,
            海南: 99,
            重庆: 99,
            四川: 99,
            贵州: 999,
            云南: 99,
            西藏: 99,
            陕西: 99,
            甘肃: 99,
            青海: 99,
            宁夏: 99,
            新疆: 99,
          },
        ], // license表格数据
      },
      }
    },
    methods:{
      cellStyle(row){//根据情况显示背景色
        if(row.column.label==="程序版本"){
          return 'background:#2D5AB9'
        }else if(row.column.label==="受理合计"){
          return 'background:#974356'
        }
      }
    }
  
  }
  </script>
  
  <style lang="scss" scoped>
  
  #compositeLeftMiddle {

    //background-color: red;
  
    ::v-deep .cell{
      padding: 0;
      color:#fff;
    }
    ::v-deep .el-table__header th {
      padding: 0;
      height: 30px;
      line-height: 30px;
  
    }
    ::v-deep .el-table__body tr,
    ::v-deep.el-table__body td {
      padding: 0;
      height: 30px;
      line-height: 30px;
    }
  
    ::v-deep .el-table {
      background-color: transparent !important;
      color: #fff !important;
    }
  
    ::v-deep .el-table__expanded-cell {
      background-color: transparent !important;
    }
  
    ::v-deep .el-table th,
    ::v-deep .el-table tr,
    ::v-deep .el-table td {
      background-color: transparent;
    }
  }
  
  </style>
