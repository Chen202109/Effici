<template>
  <div>
    <el-form :inline="true" :model="searchForm" class="search-form">
      <el-form-item v-if=false label="状态">
        <el-select v-model="searchForm.status">
          <el-option label="未解决" value="未解决"></el-option>
          <el-option label="解决中" value="解决中"></el-option>
          <el-option label="已解决" value="已解决"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="登记日期">
        <el-date-picker
          type="daterange"
          :clearable="false"
          v-model="searchForm.dateRange"
          style="width:280px"
          format="yyyy-MM-dd"
          value-format="yyyy-MM-dd"
          @change="changeDate($event)"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
        ></el-date-picker>
      </el-form-item>
      <!-- 问题分类 errortype -->
      <el-form-item label="问题分类">
        <el-select v-model="searchForm.errortype"  style="width:130px" :clearable="true" placeholder="请选择">
        <el-option
          v-for="item in errortype_list"
          :key="item.value"
          :label="item.label"
          :value="item.value">
        </el-option>
        </el-select>
      </el-form-item>
      <!-- 问题描述 problem -->
      <el-form-item label="问题描述">
        <el-input v-model="searchForm.problem"  placeholder="请输入问题描述内容"></el-input>
      </el-form-item>

      <el-form-item v-if=false label="程序版本号">
        <el-cascader
          v-model="searchForm.softversion"
          :options="regionOptions"
          change-on-select
        ></el-cascader>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="search">查询</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      searchForm: {
        status: "",
        //new Date().getFullYear(); //获取完整的年份(4位,1970-????)
        //new Date().getMonth(); //获取当前月份(0-11,0代表1月)
        //最终获得是这样 new Data('2023-07-01')
        dateRange: [new Date((new Date().getFullYear())+'-'+(new Date().getMonth()+1)+'-01'), new Date()],
        softversion: [], // 程序版本号初始值
        problem:"", // 问题描述初始值
        errortype: '', // 问题分类初始值
      },
      regionOptions: [
        {
          value: "beijing",
          label: "V4.0.4.7",
          children: [
            {
              value: "dongcheng",
              label: "V4.0.4.7_01",
            },
            {
              value: "xicheng",
              label: "V4.0.4.7_02",
            },
          ],
        },
        {
          value: "shanghai",
          label: "V4.3.1.0",
          children: [
            {
              value: "pudong",
              label: "V4.3.1.0",
            },
            {
              value: "minhang",
              label: "V4.3.1.1",
            },
            {
              value: "minhang",
              label: "V4.3.1.2",
            },
          ],
        },
      ],
      errortype_list: [{
          value: '产品BUG',
          label: '产品BUG'
        }, {
          value: '实施配置',
          label: '实施配置'
        }, {
          value: '异常数据处理',
          label: '异常数据处理'
        }],
    };
  },
  methods: {
    search() {
      // 触发查询事件，将筛选条件传给父组件
      var searchValue = {};
      // this.$emit("search", this.searchForm); //传递数据给父组件的原代码
      console.log('searchValue类型为',typeof(searchValue))
      // 获取年、月、日 ,并赋值到 searchValue 传递给父组件
      for (let i = 0; i < this.searchForm.dateRange.length; i++) {
          var year = this.searchForm.dateRange[i].getFullYear();
          var month = ("0" + (this.searchForm.dateRange[i].getMonth() + 1)).slice(-2);
          var day = ("0" + this.searchForm.dateRange[i].getDate()).slice(-2);

        if (i==0){
          // 构建格式化后的日期字符串
          var beginData = year + "-" + month + "-" + day;
          searchValue['beginData'] = beginData;
        }
        if (i==1){
          var endData = year + "-" + month + "-" + day;
          searchValue['endData'] = endData;
        }
      }
      //查询事件，将问题描述的查询内容赋值
      searchValue['problem'] = this.searchForm.problem;
      //查询事件，将问题分类 的赋值
      searchValue['errortype'] = this.searchForm.errortype;
      // $emit 可以传递参数给父组件
      this.$emit("search", searchValue);
      console.log(typeof(searchValue),'子组件向父组件传递信息为',searchValue);
    },

    // 日期控件中日期改变事件，赋值给日期控件绑定的 searchForm.dateRange
    changeDate(val) {
      //alert("选择的日期是：" + val);
      this.$message.error("选择日期完成：" + val +'可以点查询')
      //console.log(val);
      
      //由于 el-date-picker 中间的清除属性clearable默认为true, 设置方式是   :clearable="false"
      //这个属性是Boolean变量，点了叉叉清除后会导致 v-model绑定的值变成null，引起后续报错，所以调用前重新赋值
      if (!this.searchForm.dateRange) {
        console.log('出现清空日期,现在改的还是不行，还是会报错，先保留')
        this.searchForm.dateRange = ['2023-08-16', '2023-08-18']
        console.log('this.searchForm.dateRange为',this.searchForm.dateRange)
      }

      // 将所选的日期，传给时间控件 el-date-picker 通过v-model绑定的变量
      this.searchForm.dateRange[0]=new Date(val[0])
      this.searchForm.dateRange[1]=new Date(val[1])
    },
  },
};
</script>

<style scoped>
.search-form {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}
</style>
