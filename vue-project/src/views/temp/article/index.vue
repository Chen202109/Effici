<template>
  <el-form ref="form" :model="form" label-width="80px">  
	<el-form-item label="选择模板">
	          <el-select @change="selectChanged" v-model="template" placeholder="请选择模板">
            <el-option
              v-for="item in templates"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            >
            </el-option>
          </el-select>
    </el-form-item>
  </el-form>
</template>

<script>
export default {
  data() {
    return {
	templates: [{
          value: "选项1",
          label: "黄金糕",
        },
        {
          value: "选项2",
          label: "双皮奶",
        }],
	template :"",
    };
  },
  methods: {
  },
  mounted() {
    //页面初始化方法
//    this.$http
//      .get("/jira")
//      .then((response) => {
//        console.log("articel成功" +response.data);
//      })
//      .catch(function (error) {
//        console.log("articel失败"+templates.value + error);
//      });
   console.log("开始article");
   this.templates.push({value: "选项3",label: "美赞臣"});
   console.log(this.templates[2].value);
   for (var j=0; j<this.templates.length;j++){
	var name = this.templates[j].label;
	console.log(name)
   }
  },
};
</script>