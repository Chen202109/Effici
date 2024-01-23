<template>
  <div>
    <el-form :model="searchForm" class="searchForm" label-width="80px">
      <el-row>
        <el-col :span="6">
          <el-form-item label="问题分类">
            <el-input v-model="searchForm.errorType" :clearable="true" placeholder="请输入问题分类"></el-input>
          </el-form-item>
          <!-- 出错功能 errorfunction -->
          <el-form-item label="出错功能">
            <el-select v-model="searchForm.errorFunction" :clearable="true" placeholder="请选择">
              <el-option v-for="(item, index) in errorFunctionOptions" :key="index" :label="item" :value="item">
              </el-option>
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="是否解决">
            <el-select v-model="searchForm.isSolved" :clearable="true" placeholder="请选择">
              <el-option v-for="(item, index) in isSolvedList" :key="index" :label="item" :value="item">
              </el-option>
            </el-select>
          </el-form-item>
          <!-- 问题描述 softversion -->
          <el-form-item label="程序版本">
            <el-input v-model="searchForm.softVersion" placeholder="请输入版本号"></el-input>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <!-- 问题描述 problemDescription -->
          <el-form-item label="问题描述">
            <el-input type="textarea" v-model="searchForm.problemDescription" :rows="4"
              placeholder="请输入问题描述内容"></el-input>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row>
        <el-form-item label="问题归属">
          <el-select v-model="searchForm.problemParty" :clearable="true" placeholder="请选择" style="width: 140px;" @change="problemPartyChange">
            <el-option v-for="(item, index) in this.problemPartyOptions" :key="index" :label="item" :value="item">
            </el-option>
          </el-select>
          <el-select v-model="searchForm.problemAttribution" :clearable="true" filterable placeholder="请选择" style="width: 200px;">
            <el-option v-for="(item, index) in this.problemAttributionOptions" :key="index" :label="item" :value="item">
            </el-option>
          </el-select>
        </el-form-item>
      </el-row>

      <el-row>
        <el-form-item label="时间范围">
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期"
            end-placeholder="结束日期">
          </el-date-picker>
          <el-button type="primary" @click="search(true)">查询</el-button>
        </el-form-item>
      </el-row>

    </el-form>

  </div>
</template>

<script>
export default {
  name: "RecordSearchFilter",
  props: {
    errorFunctionOptions: {
      type: Array,
      default() {
        return [];
      },
    },
    problemAttributionOptionsDict: {
      type: Object,
      default() {
        return {};
      },
    }
  },
  data() {
    return {
      searchForm: {
        beginData: '', // 起始日期
        endData: '', //结束日期
        softVersion: '', // 程序版本号初始值
        errorFunction: '', //出错功能初始值
        errorType: '', // 问题分类初始值
        isSolved: '', // 是否解决初始值
        problemDescription: "", // 问题描述初始值
        problemParty: "",
        problemAttribution: ""
      },
      // 默认为最近一周的
      dateRange: [new Date(new Date().setDate(new Date().getDate() - 7)), new Date()],
      errorTypeList: ["产品BUG", "实施配置", "异常数据处理", "需求", "需求未覆盖", "重大生产事故", "安全漏洞", "his传参错误"],
      isSolvedList: ["是", "否"],
      problemPartyOptions: [],
      problemAttributionOptions: [],
    };
  },
  watch: {
    problemAttributionOptionsDict: {
      handler(newVal, oldVal) {
        this.problemPartyOptions = Object.keys(newVal)
        this.problemPartyChange()
      }
    }
  },
  methods: {

    /**
     * 选择问题分类的出错方，同步出错方对应的问题分类的具体属性
     * @param {*} value 
     */
    problemPartyChange(value) {
      this.searchForm.problemAttribution = ''
      this.problemAttributionOptions = this.problemAttributionOptionsDict[this.searchForm.problemParty]
    },

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
        searchValue[(i == 0) ? "beginData" : "endData"] = year + "-" + month + "-" + day;
      }
      searchValue["requestTotal"] = requestTotal;
      console.log('子组件向父组件传递信息为', searchValue);
      // $emit 可以传递参数给父组件
      this.$emit("search", searchValue);
    },
  },
};
</script>

<style scoped>
.searchForm {
  align-items: center;
}

.el-form-item .el-select {
  width: 100%;
}
</style>
