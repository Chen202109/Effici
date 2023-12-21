<template>
  <div>
    <el-form ref="workRecordEditForm" :rules="rules" :model="form" label-width="100px" size="small">
      <!-- 所有el-row最后里面的col总和为span 23,因为如果设置成24的话，左右边会不对称，因为左边有留给el-form-item的label的空间，但是右边没有，
        会直接元素和关闭的叉叉靠的太近 -->
      <el-row>
        <el-col :span = 7>
          <el-form-item label="是否解决" prop="isSolved">
            <el-select v-model="form.isSolved" clearable placeholder="请选择">
              <el-option v-for="(item, index) in isSolvedOptions" :key="index" :label="item" :value="item">
              </el-option>
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span = 8>
          <el-form-item label="登记日期" prop="registerDate">
            <el-date-picker class="datePicker" v-model="form.registerDate" type="date" placeholder="请输入"></el-date-picker>
          </el-form-item>
        </el-col>
        <el-col :span = 8>
          <el-form-item label="解决日期" prop="solveDate">
            <el-date-picker class="datePicker" v-model="form.solveDate" type="date" placeholder="请输入"></el-date-picker>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row>
        <el-col :span = 7>
          <el-form-item label="省份" prop="province">
            <el-input v-model="form.province" placeholder="请输入省份"></el-input>
          </el-form-item>
        </el-col>
        <el-col :span = 8>
          <el-form-item label="接入方" prop="informParty">
            <el-input v-model="form.informParty" placeholder="请输入"></el-input>
          </el-form-item>
        </el-col>
        <el-col :span = 8>
          <el-form-item label="接入人" prop="informer">
            <el-input v-model="form.informer" placeholder="请输入"></el-input>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row>
        <el-col :span = 23>
          <el-form-item label="单位名称" prop="agencyName">
            <el-input v-model="form.agencyName" placeholder="请输入单位名称"></el-input>
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row>
        <el-col :span = 7>
          <el-form-item label="出错功能" prop="errorFunction">
            <el-select v-model="form.errorFunction" clearable placeholder="请选择">
              <el-option v-for="(item, index) in errorFunctionOptions" :key="index" :label="item" :value="item"></el-option>
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row>
        <el-col :span = 7>
          <el-form-item label="环境" prop="environment">
            <el-select v-model="form.environment" clearable placeholder="请选择">
              <el-option v-for="(item, index) in environmentOptions" :key="index" :label="item" :value="item"></el-option>
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span = 16>
          <el-form-item label="问题分类" prop="problemType">
            <el-col :span="9">
              <el-select v-model="form.problemTypeParty" clearable placeholder="请选择" @change="problemTypePartyChange">
                <el-option v-for="(item, index) in problemTypePartyOptions" :key="index" :label="item" :value="item"></el-option>
              </el-select>
            </el-col>
            <el-col :span = 2 style="border: 1px solid transparent;"></el-col>
            <el-col :span="13">
              <el-select v-model="form.problemType" clearable placeholder="请选择">
                <el-option v-for="(item, index) in problemTypeOptions" :key="index" :label="item" :value="item"></el-option>
              </el-select>
            </el-col>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row>
        <el-col :span = 23>
          <el-form-item label="问题归属" prop="problemAttribution">
            <el-input v-model="form.problemAttribution" placeholder="请输入问题归属, 格式如: 开票管理-批量开票-程序bug"></el-input>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row>
        <el-col :span = 7>
          <el-form-item label="产品类型" prop="productType">
            <el-select v-model="form.productType" clearable placeholder="请选择">
              <el-option v-for="(item, index) in productTypeOptions" :key="index" :label="item" :value="item"></el-option>
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span = 8>
          <el-form-item label="数据库类型" prop="databaseType">
            <el-select v-model="form.databaseType" clearable placeholder="请选择">
              <el-option v-for="(item, index) in databaseTypeOptions" :key="index" :label="item" :value="item"></el-option>
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span = 8>
          <el-form-item label="程序版本号" prop="softVersion">
            <el-input v-model="form.softVersion" placeholder="请输入"></el-input>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row>
        <el-col :span = 7>
          <el-form-item label="处理人" prop="solver">
            <el-input v-model="form.solver" placeholder="请输入"></el-input>
          </el-form-item>
        </el-col>
        <el-col :span = 8>
          <el-form-item label="处理耗时" prop="timeSpent">
            <el-input v-model="form.timeSpent" placeholder="请输入"></el-input>
          </el-form-item>
        </el-col>
        <el-col :span = 8>
          <el-form-item label="JIRA编号" prop="JIRAId">
            <el-input v-model="form.JIRAId" placeholder="请输入"></el-input>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row>
        <el-col :span = 23>
          <el-form-item label="问题描述" prop="problemDescription">
            <!-- :4代表这个textarea可以展示四行的内容 -->
            <el-input type="textarea" :rows="4" v-model="form.problemDescription"></el-input>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row>
        <el-col :span = 23>
          <el-form-item label="解决方案" prop="solution">
            <el-input type="textarea" v-model="form.solution"></el-input>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row>
        <el-col :span = 23>
          <el-form-item label="原因分析" prop="reasonAnalysis">
            <el-input type="textarea" v-model="form.reasonAnalysis"></el-input>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row>
        <!-- 因为如果直接text-align-center的话，他是对应span 24的布局，会偏移整个表单的中心 -->
        <el-col :span = 23>
          <el-form-item style="text-align: center;">
            <el-button size=“medium” type="primary" @click="submitForm('workRecordEditForm')">提交</el-button>
            <el-button size=“medium” @click="resetForm('workRecordEditForm')">重置</el-button>
          </el-form-item>
        </el-col>
        <el-col :span = 1></el-col>
      </el-row>

    </el-form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      form: {
        isSolved: '',
        registerDate: '',
        solveDate : '',
        province:'',
        informParty: '',
        solver : '',
        agencyName: '',
        productType: '',
        environment: '',
        errorFunction: '',
        problemAttribution: '',
        problemTypeParty: '',
        problemType : '',
        informer : '',
        databaseType: '',
        softVersion: '',
        JIRAId: '',
        problemDescription: '',
        solution: '',
        reasonAnalysis:'',
        timeSpent :'',
      },

      rules: {
        isSolved: [
          { required: true, message: '请输入是否解决', trigger: 'blur' }
        ],
        registerDate: [
          { type: 'date', required: true, message: '请选择日期', trigger: 'change' }
        ],
        solveDate : [],
        province: [
          { required: true, message: '请输入省份', trigger: 'blur' },
          { max: 5, message: '省份长度在 5 个字符内', trigger: 'blur' }
        ],
        informParty: [],
        solver : [],
        agencyName: [
          { required: true, message: '请输入单位名称', trigger: 'blur' }
        ],
        productType: [
          { required: true, message: '请选择产品类型', trigger: 'blur' }
        ],
        errorFunction: [
          { required: true, message: '请选择出错功能', trigger: 'blur' }
        ],
        problemAttribution: [],
        environment: [
          { required: true, message: '请选择公/私有化', trigger: 'blur' }
        ],
        problemTypeParty: [],
        problemType : [],
        informer : [],
        databaseType: [
          { required: true, message: '请选择数据库类型', trigger: 'blur' }
        ],
        softVersion: [
          { required: true, message: '请输入版本号', trigger: 'blur' },
          { pattern: /^V[34]\.\d+(\.\d+){2}$/, message: '格式为Vx.x.x.x, 例如V4.3.2.1', trigger: 'blur'}
        ],
        JIRAId: [],
        problemDescription: [
          { max: 650, message: '问题描述过长，请去掉多余部分如日志信息等', trigger: 'blur' }
        ],
        solution: [],
        reasonAnalysis: [],
        timeSpent : [],
      },

      isSolvedOptions: ["是","否"],
      productTypeOptions: ['医疗', '高校', '通用', '捐赠', '增值', '工会'],
      environmentOptions : ["公有云", "私有化"], 
      errorFunctionOptions: ["开票功能","核销功能","收缴业务","通知交互","报表功能","数据同步","票据管理","license重置","单位开通","增值服务","打印功能","安全漏洞","反算功能", "基础功能"],
      problemTypePartyOptions : ["财政", "行业"],
      problemTypeOptionsDict : {
        "" : [],
        "财政" : ["交互服务", "基础信息","制票中心", "数据同步", "票据审验状态异常", "缴款确认状态异常", "出库状态异常", "库存重复", "收入退付状态异常", "需求变更", "第三方入参异常"],
        "行业" : ["程序BUG", "数据问题-日结", "数据问题-V3迁移V4", "数据问题-数据反算", "数据问题-BUG导致异常数据", "业务-沟通", "业务-需求不满足", "业务-V3需求未覆盖", "业务-用户操作不当", "实施运维-操作失误", "实施运维-常规配置调整", "实施运维-环境部署", "实施运维-增值开通", "实施运维-协助数据处理", "实施运维-license状态重置", "第三方入参异常"], 
      },
      // problemTypeOptions: ["产品BUG","实施配置","异常数据处理", "需求", "需求未覆盖", "重大生产事故", "安全漏洞", "his传参错误"],
      problemTypeOptions: "",
      databaseTypeOptions: ["TDSQL", "MYSQL", "ORACLE", "达梦", "人大金仓"],
    }
  },

  mounted() {
    this.problemTypeOptions = this.problemTypeOptionsDict[this.form.problemTypeParty]
  },
  methods: {

    /**
     * 选择问题分类的出错方，同步出错方对应的问题分类的具体属性
     * @param {*} value 
     */
    problemTypePartyChange(value) {
      this.form.problemType = ''
      this.problemTypeOptions = this.problemTypeOptionsDict[this.form.problemTypeParty]
    },

    /**
     * 提交表单数据
     * @param {*} formName 
     */
    submitForm(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          // 触发提交事件，将表单数据传给父组件
          this.$emit('submit', this.form)
        } else {
          console.log('error submit!!');
          return false;
        }
      });
    },

    /**
     * 重置表单数据
     * @param {*} formName 
     */
    resetForm(formName) {
      this.$refs[formName].resetFields();
    }
  }
}
</script>


<style>

.datePicker {
  width: 100% !important
}

</style>