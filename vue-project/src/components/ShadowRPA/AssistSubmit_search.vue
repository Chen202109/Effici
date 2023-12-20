<template>
  <div>
    <el-form :inline="true" :model="searchForm" class="searchForm">

      <!-- 问题分类 errortype -->
      <el-form-item label="问题分类">
        <el-select v-model="searchForm.errorType"  style="width:130px" :clearable="true" placeholder="请选择">
          <el-option v-for="(item, index) in errorTypeList" :key="index" :label="item" :value="item">
          </el-option>
        </el-select>
      </el-form-item>
      <!-- 出错功能 errorfunction -->
      <el-form-item label="出错功能">
        <el-select v-model="searchForm.errorFunction" style="width:120px" :clearable="true" placeholder="请选择">
          <el-option v-for="(item, index) in errorFunctionList" :key="index" :label="item" :value="item">
          </el-option>
        </el-select>
      </el-form-item>
      <!-- 是否解决 issolve -->
      <el-form-item label="是否解决">
        <el-select v-model="searchForm.isSolved"  style="width:90px" :clearable="true" placeholder="请选择">
          <el-option v-for="(item, index) in isSolvedList" :key="index" :label="item" :value="item">
          </el-option>
        </el-select>
      </el-form-item>
      <!-- 问题描述 problemDescription -->
      <el-form-item label="问题描述">
        <el-input v-model="searchForm.problemDescription" placeholder="请输入问题描述内容"></el-input>
      </el-form-item>
      <!-- 问题描述 softversion -->
      <el-form-item label="程序版本号">
        <el-input v-model="searchForm.softVersion" placeholder="请输入版本号"></el-input>
      </el-form-item>

      <el-form-item label="日期">
        <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" >
        </el-date-picker>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="search(true)">查询</el-button>
      </el-form-item>

    </el-form>
  </div>
</template>
errorType
<script>
export default {
  data() {
    return {
      searchForm: {
        beginData : '', // 起始日期
        endData : '', //结束日期
        softVersion: '', // 程序版本号初始值
        errorFunction: '', //出错功能初始值
        errorType: '', // 问题分类初始值
        isSolved: '', // 是否解决初始值
        problemDescription:"", // 问题描述初始值
      },
      // 默认为最近一周的
      dateRange: [new Date(new Date().setDate(new Date().getDate() - 7)), new Date()],
      errorTypeList: ["产品BUG","实施配置","异常数据处理"],
      errorFunctionList: ["开票功能","核销功能","收缴业务","通知交互","报表功能","数据同步","票据管理","license重置","单位开通","增值服务","打印功能","安全漏洞","反算功能"],
      isSolvedList: ["是","否"],
    };
  },
  methods: {
    
    /**
     * 触发查询事件，将筛选条件传给父组件
     * @param {boolean} requestTotal 看是否需要请求总条目值，如果是正常点search按钮需要，如果是翻页跳转不需要 
     */
    search(requestTotal) {
      var searchValue = this.searchForm;
      // 获取年、月、日 ,并赋值到 searchValue 传递给父组件
      for (let i = 0; i < this.dateRange.length; i++) {
        var year = this.dateRange[i].getFullYear();
        var month = ("0" + (this.dateRange[i].getMonth() + 1)).slice(-2);
        var day = ("0" + this.dateRange[i].getDate()).slice(-2);
        searchValue[(i==0)?"beginData":"endData"] = year + "-" + month + "-" + day;
      }
      searchValue["requestTotal"] = requestTotal;
      console.log('子组件向父组件传递信息为',searchValue);
      // $emit 可以传递参数给父组件
      this.$emit("search", searchValue);
    },
  },
};
</script>

<style scoped>
.searchForm {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}
</style>
