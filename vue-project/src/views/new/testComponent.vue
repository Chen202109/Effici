<template>
  <el-container>
    <div style="width: 323px">
      <el-form
        :model="ruleForm"
        :rules="rules"
        ref="ruleForm"
        label-width="100px"
        class="demo-ruleForm"
        size="mini"
      >
        <el-form-item label="模板名称" prop="title">
          <el-input v-model="ruleForm.title"></el-input>
        </el-form-item>

        <el-form-item label="项目" prop="project">
          <el-select v-model="ruleForm.project" placeholder="请选择项目">
            <el-option
              label="35-非税票据产品"
              value="35-非税票据产品"
            ></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="问题类型" prop="type">
          <el-select v-model="ruleForm.type" placeholder="请选择问题类型">
            <el-option label="BUG及数据问题" value="BUG及数据问题"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="省份" prop="region">
          <el-select v-model="ruleForm.region" placeholder="请选择省份">
            <el-option label="000000 财政部" value="000000 财政部"></el-option>
            <el-option label="350000 福建省" value="350000 福建省"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="经办人" prop="handler">
          <el-input v-model="ruleForm.handler"></el-input>
        </el-form-item>

        <el-form-item label="主题前缀" prop="prefix">
          <el-input v-model="ruleForm.prefix"></el-input>
        </el-form-item>

        <el-form-item label="环境描述" prop="environment">
          <el-input
            type="textarea"
            rows="7"
            v-model="ruleForm.environment"
          ></el-input>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitForm('ruleForm')"
            >保存JIRA模板</el-button
          >
          <el-button type="info" @click="resetForm('ruleForm')">重填</el-button>
        </el-form-item>
      </el-form>
    </div>
    <el-aside width="20px">1111111</el-aside>

    <el-div style="width: 420px">
      <el-form ref="form" :model="form"  label-width="80px" >
        <el-form-item label="用户" prop="user">
          <div style="width: 180px">
            <el-input placeholder="请输入用户" v-model="form.user"></el-input>
          </div>
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <div style="width: 180px">
            <el-input
              placeholder="请输入密码"
              v-model="form.password"
              show-password
            ></el-input>
          </div>
        </el-form-item>

        <el-form-item label="选择模板">
          <el-select
            @change="selectChanged"
            v-model="form.template"
            placeholder="请选择模板"
          >
            <el-option
              v-for="item in templates"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            >
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="主题" prop="theme">
          <div style="width: 420px">
            <el-input v-model="form.theme"></el-input>
          </div>
        </el-form-item>

        <el-form-item label="问题描述" prop="describe">
          <div style="width: 420px">
            <el-input
              type="textarea"
              rows="8"
              v-model="form.describe"
            ></el-input>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button
            type="warning"
            @click="submitForm('ruleForm')"
            icon="el-icon-upload"
            >上传附件enclosure</el-button
          >
          <el-button type="success" @click="submitForm('ruleForm')"
            >登记BUG</el-button
          >
        </el-form-item>
      </el-form>
    </el-div>
  </el-container>
</template>
<script>
export default {
  data() {
    return {
      templates: [
        {
          value: "选项1",
          label: "财政票据中心监控2.1",
          title: "",
          project: "",
          type: "",
          region: "",
          handler: "",
          prefix: "",
          environment: "",
        },
      ],
      ruleForm: {
        title: "财政票据中心监控2.1",
        type: "BUG及数据问题",
        project: "35-非税票据产品",
        region: "000000 财政部",
        handler: "林信康",
        prefix: "【专利局-国产化适配】",
        environment:
          "专利局网站地址" +
          "\n" +
          "http://172.18.166.234:7001/standard-web/main.do" +
          "\n" +
          "用户001  密码1",
      },
      form: {
        user: "",
        password: "",
        template: "",
        theme: "",
        describe: "",
      },
      rules: {
        title: [
          { required: true, message: "请输入要保存的标题", trigger: "blur" },
          {
            min: 2,
            max: 100,
            message: "长度在 2 到 100 个字符",
            trigger: "blur",
          },
        ],
        region: [{ required: true, message: "请选择省份", trigger: "change" }],
        type: [
          { required: true, message: "请选择问题类型", trigger: "change" },
        ],
        project: [
          { required: true, message: "请选择问题类型", trigger: "change" },
        ],
        handler: [
          { required: true, message: "请输入经办人", trigger: "blur" },
          {
            min: 2,
            max: 10,
            message: "长度在 2 到 10 个字符",
            trigger: "blur",
          },
        ],
        prefix: [
          { required: true, message: "请输入主题前缀", trigger: "blur" },
        ],
        environment: [
          { required: true, message: "请输入描述环境信息", trigger: "blur" },
        ],
      },
    };
  },
  methods: {
    submitForm(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          alert("submit!提交成功");
        } else {
          console.log("error submit!!");
          return false;
        }
      });
    },
    resetForm(formName) {
      this.$refs[formName].resetFields();
    },
    selectChanged(value) {
      console.log(value);
      this.ruleForm.title = this.templates[value - 1].title;
      this.ruleForm.project = this.templates[value - 1].project;
      this.ruleForm.type = this.templates[value - 1].type;
      this.ruleForm.region = this.templates[value - 1].region;
      this.ruleForm.handler = this.templates[value - 1].handler;
      this.ruleForm.prefix = this.templates[value - 1].prefix;
      this.ruleForm.environment = this.templates[value - 1].environment;
    },
  },
  mounted() {
    //页面初始化方法
    this.$http
      .get("/api/jira")
      .then((response) => {
        for (var j = 0; j < response.data.data.length; j++) {
          //		this.templates.push({"value":response.data.data[j].value,"label":response.data.data[j].label})

          this.templates[j].value = response.data.data[j].value;
          this.templates[j].label = response.data.data[j].label;
          this.templates[j].title = response.data.data[j].title;
          this.templates[j].project = response.data.data[j].project;
          this.templates[j].type = response.data.data[j].type;
          this.templates[j].region = response.data.data[j].region;
          this.templates[j].handler = response.data.data[j].handler;
          this.templates[j].prefix = response.data.data[j].prefix;
          this.templates[j].environment = response.data.data[j].environment;
        }
      })
      .catch(function (error) {
        console.log(error);
        alert("失败" + error);
      });
  },
};
</script>