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
		  <span>ID:{{ruleForm.project_id}}</span>
		  <span>key:{{ruleForm.project_key}}</span>
		  <span>选择模板{{dataForm.template}}</span>
        </el-form-item>

        <el-form-item label="问题类型" prop="type">
          <el-select v-model="ruleForm.type" placeholder="请选择问题类型">
            <el-option label="BUG及数据问题" value="BUG及数据问题"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="省份" prop="region">
          <el-select v-model="ruleForm.region" placeholder="请选择省份" style="width:65%">
            <el-option label="None" value="None"></el-option>
            <el-option label="000000 财政部" value="000000 财政部"></el-option>
			<el-option label="350000 福建省" value="350000 福建省"></el-option>
          </el-select>
		  <span>ID:{{ruleForm.issue_regionid}}</span>
        </el-form-item>

        <el-form-item label="经办人" prop="handler">
          <el-input v-model="ruleForm.handler"></el-input>
        </el-form-item>

        <el-form-item label="主题前缀" prop="prefix">
          <el-input v-model="ruleForm.prefix"></el-input>
        </el-form-item>
		
        <el-form-item label="产品模块" prop="issue_module">
          <el-select v-model="ruleForm.issue_module" placeholder="请选择产品模块" style="width:65%">
            <el-option label="00-应用平台管理" value="00-应用平台管理"></el-option>
          </el-select>
		  <span>ID:{{ruleForm.issue_moduleid}}</span>
        </el-form-item>
		
        <el-form-item label="严重级别" prop="issue_level">
          <el-select v-model="ruleForm.issue_level" placeholder="请选择严重级别" style="width:65%">
            <el-option label="一般" value="一般"></el-option>
          </el-select>
		  <span>ID:{{ruleForm.issue_levelid}}</span>
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
    <el-aside width="20px"></el-aside>

    <div style="width: 480px">
      <el-form ref="dataForm" :model="dataForm" label-width="80px" size="mini">
        <el-form-item label="用户" prop="user">
          <div style="width: 180px">
            <el-input placeholder="请输入用户" v-model="dataForm.user"></el-input>
          </div>
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <div style="width: 180px">
            <el-input
              placeholder="请输入密码"
              v-model="dataForm.password"
              show-password
            ></el-input>
          </div>
        </el-form-item>

        <el-form-item label="选择模板">
          <el-select
            @change="selectChanged"
            v-model="dataForm.template"
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
            <el-input v-model="dataForm.theme"></el-input>
          </div>
        </el-form-item>

        <el-form-item label="问题描述" prop="describe">
          <div style="width: 420px">
            <el-input
              type="textarea"
              rows="8"
              v-model="dataForm.describe"
            ></el-input>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button type="warning" @click="submitForm('ruleForm')" icon="el-icon-upload" :disabled=true>上传附件enclosure</el-button
          >
		  <el-button type="info" plain @click="clearSet()">清空</el-button>
		  <el-button type="primary" @click="dataSet('ruleForm','dataForm')">添加</el-button>
          <el-button ref="buttonIssue" type="success" @click="registerIssue('ruleForm')" :disabled='buttonTrue'>登记BUG</el-button>
        </el-form-item>
      </el-form>
    </div>
  </el-container>
</template>
<script>
export default {
  data() {
    return {
	  buttonTrue : true,
      //根据jira系统入参内容设置issue_dict
      templates: [
        {
          name : '', // 连接jira的用户
          password : '', //连接jira密码
          label : '黄金',  //选择模板下拉显示文本
          value : '1',  //选择模板下拉对应的值
          project: { id: 'project_id', key: 'project_key', name: 'project_name' }, // 项目
          summary: 'issue_summary', // 问题标题
          description: 'issue_description', //  问题描述
          issuetype: { name: 'issuetype_name' }, // 问题类型
          assignee: { name: 'issue_assignee' }, // 分配给谁
          customfield_10000: { value: 'issue_region', id: 'issue_regionid' }, // 区划
          customfield_10402: { value: 'issue_module', id: 'issue_moduleid' }, // 产品模块 必填
          customfield_10202: { value: 'issue_level', id: 'issue_levelid' }, // 级别默认一般
        }
      ],
      ruleForm: {
        title: "财政票据中心监控2.1",
        type: "BUG及数据问题",
        project: "35-非税票据产品",
		project_id: "10401",
		project_key: "NTBILL",
        region: "000000 财政部",
		issue_regionid: "10000",
        handler: "林信康",
		issue_module: "00-应用平台管理",
		issue_moduleid: "10401",
        prefix: "【专利局-国产化适配】",
        environment:
          "专利局网站地址" +
          "\n" +
          "http://172.18.166.234:7001/standard-web/main.do" +
          "\n" +
          "用户001  密码1",
		issue_level: '一般',
		issue_levelid: '10215',
      },
      dataForm: {
        user: "ceshi",
        password: "ccc",
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
	clearSet() {
      this.dataForm.theme = '';
	  this.dataForm.describe ='';
	  this.buttonTrue = true;    //  关闭登记bug的按钮
    },
    dataSet(formName1,formName2) {
      this.$refs[formName1].validate((valid) => {
        if (valid) {
          // 还有一个验证
		  this.$refs[formName2].validate((valid) => {
			if (valid) {
				this.dataForm.theme = this.ruleForm.prefix +this.dataForm.theme;
				this.dataForm.describe = this.ruleForm.environment+this.dataForm.describe;
				this.buttonTrue = false;   //  开启登记bug的按钮
			} else {
			console.log("error submit!!");
			return false;
			}
      })
		  // 验证结束
        } else {
          console.log("error submit!!");
          return false;
        }
      });
    },
	submitForm(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          alert("submit!功能未开发");
        } else {
          console.log("error submit!!");
          return false;
        }
      });
    },
	registerIssue(formName) {
	  this.buttonTrue = true;    //  不论成败，先禁用 登记bug的按钮
	  var issue_data ={
		name : this.dataForm.user, // 连接jira的用户
        password : this.dataForm.password, //连接jira密码
        project: {id: this.ruleForm.project_id, key: this.ruleForm.project_key, name: this.ruleForm.project},  // 项目
        summary: this.dataForm.theme,  // 问题标题
        description: this.dataForm.describe,  // 问题描述
        issuetype: {name: this.ruleForm.type},  // 问题类型
        assignee: {'name': this.ruleForm.handler},  // 分配给谁
        customfield_10000: {value: this.ruleForm.region, id: this.ruleForm.issue_regionid},  // 区划
        customfield_10402: {value: this.ruleForm.issue_module, id: this.ruleForm.issue_moduleid},  // 产品模块 必填
        customfield_10202: {value: this.ruleForm.issue_level, id: this.ruleForm.issue_levelid}  // 级别默认一般
    };
      this.$refs[formName].validate((valid) => {
	   this.$http.post("/api/jira",issue_data).then(function(response){
          alert("访问后台成功！\r\n返回信息：\r\n"+response.data.data);
      }).catch(function (error) {
        console.log(error);
        alert("失败" + error);
      })
      });
    },
    resetForm(formName) {
      this.$refs[formName].resetFields();
    },
    selectChanged(value) {
      console.log(value);
      this.ruleForm.title = this.templates[value - 1].label;  //标题
      this.ruleForm.project = this.templates[value - 1].project.name;   //项目
	  this.ruleForm.project_id = this.templates[value -1].project.id;
	  this.ruleForm.project_key = this.templates[value -1].project.key;
      this.ruleForm.type = this.templates[value - 1].issuetype.name;  //问题类型
      this.ruleForm.region = this.templates[value - 1].customfield_10000.value;   //区划
	  this.ruleForm.issue_regionid = this.templates[value - 1].customfield_10000.id;  
      this.ruleForm.handler = this.templates[value - 1].assignee.name;     //经办人
      this.ruleForm.prefix = this.templates[value - 1].summary;   //标题
      this.ruleForm.environment = this.templates[value - 1].description;    //内容
    },
  },
  mounted() {
    //页面初始化方法
    this.$http
      .get("/api/CMC/jira")
      .then((response) => {
         this.templates= response.data.data;
      })
      .catch(function (error) {
        console.log(error);
        alert("失败" + error);
      });
  },
};
</script>