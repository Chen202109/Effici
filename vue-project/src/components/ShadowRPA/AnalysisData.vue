<template>
  <!-- 所有的内容要被根节点包含起来-->
  <div id="news">
    <!-- 放入查询条件的组件 -->
    <div>
      <template>
        <div class="block">
          <span class="demonstration">分析范围： </span>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          >
          </el-date-picker>
          <el-button type="primary" @click="search">查询</el-button>
        </div></br>
      </template>
      <!-- 周末要发的受理信息数据-->
      <div>受理问题总共 <span style="color: red;">{{all_total}}次</span>，其中bug数量为：<span style="color: red;">{{all_softbug}}个</span>，
      实施配置：<span style="color: red;">{{all_sspz}}个</span>，异常数据处理：<span style="color: red;">{{all_ycsjcl}}次</span> </div>
      <!-- 临时放入table 组件 style="font-size: 10px; width: 100%"-->
      <template>
        <el-table :data="analysisData['tableData']" :row-style="{ height: '40px' }" :cell-style="{padding:'0px'}"
          :header-cell-style="{fontSize:'14px',background:'#DDDDDD',color:'#696969'}" style="font-size: 18px; width: 100% " Boolean border show-summary>
          <el-table-column prop="softversion" label="程序版本" width="100" align="center" > </el-table-column>
          <el-table-column prop="total" label="合计" width="80" align="center" > </el-table-column>
          <el-table-column prop="report" label="报表功能" width="80" align="center" > </el-table-column>
          <el-table-column prop="openbill" label="开票功能" width="80" align="center" > </el-table-column>
          <el-table-column prop="licenseReset" label="license重置" width="100" align="center" > </el-table-column>
          <el-table-column prop="added" label="增值服务" width="80" align="center" > </el-table-column>
          <el-table-column prop="collection" label="收缴业务" width="80" align="center" > </el-table-column>
          <el-table-column prop="exchange" label="通知交互" width="80" align="center" > </el-table-column>
          <el-table-column prop="writeoff" label="核销功能" width="80" align="center" > </el-table-column>   
          <el-table-column prop="billManagement" label="票据管理" width="80" align="center" > </el-table-column>   
          <el-table-column prop="security" label="安全漏洞" width="80" align="center" > </el-table-column>   
          <el-table-column prop="print" label="打印功能" width="80" align="center" > </el-table-column>   
          <el-table-column prop="datasync" label="数据同步" width="80" align="center" > </el-table-column>   
          <el-table-column prop="inverse" label="反算功能" width="80" align="center" > </el-table-column>
          <el-table-column prop="opening" label="单位开通" width="80" align="center" > </el-table-column>
          <el-table-column prop="softbug" label="缺陷合计" width="80" align="center" style="font-size: 30px; width: 100% "> </el-table-column>         
        </el-table>
      </template>
    </div>
    <!-- 放入Echarts 可视化图形 组件 -->
    </br>
    <div class="myChart" id="myChart" :style="{ width: '750px', height: '450px' }"></div>
    <div class="annularChart" id="annularChart" :style="{ width: '600px', height: '450px' }"></div>
    <br />
    <!-- 放入license的数据组件 -->
    <div>
      <license :licenseData="analysisData['licenseData']"></license>      
    </div>
    </br>
    <!-- 放入upgrade 资源池升级数据组件 -->
    <div style="float: left; margin-right: 20px;">
      <upgrade :upgradeData="analysisData['upgradeData']"></upgrade>
    </div>
    <div style="float: left;">
      <el-button v-if="showForm != true" type="primary" @click="showForm = true">查看问题分类统计</el-button>
      <el-table  v-if="showForm" :data="analysisData['tableData']" :header-cell-style="{ background:'#DDDDDD',color:'#000'}" 
        :row-style="{ height: '25px' }" :cell-style="{padding:'0px'}" border style="width: 100%" show-summary>
        <el-table-column prop="softversion" label="程序版本" width="100" align="center" > </el-table-column>
        <el-table-column prop="softbug" label="产品bug" width="80" align="center" > </el-table-column>
        <el-table-column prop="sspz" label="实施配置" width="80" align="center" > </el-table-column>   
        <el-table-column prop="ycsjcl" label="异常数据处理" width="110" align="center" > </el-table-column>   
      </el-table>  
    </div>
  </div>
</template>

<script>
import license from '@/components/ShadowRPA/AnalysisData_license.vue'
import upgrade from '@/components/ShadowRPA/AnalysisData_upgrade.vue'

// 引入基本模板
let echarts = require("echarts/lib/echarts");
// 引入柱状图组件
require("echarts/lib/chart/bar");
// 引入提示框和title组件
require("echarts/lib/component/tooltip");
require("echarts/lib/component/title");
export default {
  name: "AnalysisData",
    components: {
    license,
    upgrade
  },
  data() {
    return {
      showForm: false, // 控制显示隐藏问题分类的图表
      all_total : 0,all_softbug:0, all_sspz:0, all_ycsjcl:0, // 本范围受理总数、产品bug、实施配置、异常数据处理
      //查询日期
      dateRange: [new Date((new Date().getFullYear())+'-'+(new Date().getMonth()+1)+'-01'), new Date()],
      // 通过this.$http.get 请求analysisselect 返回的 分析analysis 数据data
      analysisData:{
        // tableData 受理表格数据
        'tableData':[{added:"0",billManagement:"1",collection:"1",datasync:"1",exchange: "2",inverse:"1",licenseReset:"0",openbill: "4",opening:"0",print:"1",report:"2",security:"0",softversion:"V3",total: "13",writeoff:"0",softbug:"2"}],
        // upgradeData 升级计划表格的数据
        "upgradeData":[{resourcepool: "01资源池", 缺陷: "6", 需求: "2", 优化: "0"}], // 升级表格数据
        // licenseData license表格的数据
        'licenseData':[{
          省份: '申请单位数',
          北京: 999, 山西: 99, 内蒙古: 99, 辽宁: 99, 吉林: 99, 黑龙江:99, 上海: 99, 安徽:99, 福建:99,
          江西: 999, 山东: 99, 河南: 99, 湖北: 99, 广东: 99, 广西:99, 海南: 99, 重庆:99, 四川:99,
          贵州: 999, 云南: 99, 西藏: 99, 陕西: 99, 甘肃: 99, 青海:99, 宁夏: 99, 新疆:99
        },] // license表格数据
      },
    }
  },
  // 计算合计属性
 computed: {
    data() {

    }
  },
  // 在初始化页面完成后,再对dom节点上图形进行相关绘制
  mounted() {
    this.drawLine();
  },

  methods: {
    // 进行Echarts的图形绘制
    drawLine() {
      // 基于准备好的dom，初始化echarts实例
      let myChart = echarts.init(document.getElementById("myChart"));
      let annularChart = echarts.init(document.getElementById("annularChart"));

      // 绘制柱形图形
      myChart.setOption({
        color: ['#3398DB'], // 设置柱形图颜色
        //设置 title 的 字体大小 和颜色
        title: {
          text: "SaaS各版本受理汇总",
          left: 'left',
          top: '1%',
          textStyle: {
            fontSize: 20,
            fontWeight: 'normal',
            fontStyle: 'normal',
            color: '#3398DB'
          }
        },
        tooltip: {
          //设置鼠标悬停提示框的位置。
          //   trigger: 'axis',
          //   position: [20, 20]
          //   // 等价于
          //   // position: ['20px', '20px']
        },
        xAxis: {
           data: [
            "V3",
            "V4.0.4.7",
            "V4.3.1.0",
            "V4.3.1.2",
            "V4.0.4.6",
            "V4.0.4.5",
          ],
        },
        yAxis: {},
        series: [
          {
            name: "数量",
            type: "bar",
            data: [5, 20, 36, 10, 10, 20],
            // label 是说是否显示柱形图上的数值，position 表示数值的位置
            label: {
              show: true,
              position: 'top',
              //字体大小
              fontSize: 14,
            },
          },
        ],
      }),
      // 绘制饼状的图形
      annularChart.setOption({
        tooltip: { trigger: 'item' },
        legend: {
          top: '2%',
          left: 'center'
        }, 
        series: [
          {
          name: '受理数量',
          type: 'pie',
          radius: ['30%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
          },
          label: {
            show: true, // 是否显示标签
            formatter: '{b} : {d}%',  // 格式化标签内容
            position: 'inside', // 设置标签位置为内部
            fontSize: 12 // 设置标签字体大小为14px
          },
          emphasis: {
            label: {
            show: true,
            fontSize: 40,
            fontWeight: 'bold'
            }
            },
          labelLine: {
            show: false
            },
        data: [
          { value: 1048, name: '报表功能' },
          { value: 735, name: '开票功能' },
          { value: 580, name: 'license重置' },
          { value: 484, name: '增值服务' },
          { value: 300, name: '收缴业务' },
          { value: 1048, name: '通知交互' },
          { value: 735, name: '核销功能' },
          { value: 580, name: '票据管理' },
          { value: 484, name: '安全漏洞' },
          { value: 300, name: '打印功能' },
          { value: 484, name: '数据同步' },
          { value: 300, name: '反算功能' },
          { value: 300, name: '单位开通' },
          ]
          }],

      })
    },
    // 结束echarts图形绘制
    
    // 进行 查询 事件,因为axios是异步的请求，所以会先处理数据，空闲了才处理异步数据
    async search(){
      // 触发查询事件，根据日期条件进行查询
      var searchValue = {};      // 存放筛选条件信息
      // 获取年、月、日，进行拼接
      for (let i = 0; i < this.dateRange.length; i++) {
          var year = this.dateRange[i].getFullYear();
          var month = ("0" + (this.dateRange[i].getMonth() + 1)).slice(-2);
          var day = ("0" + this.dateRange[i].getDate()).slice(-2);

        if (i==0){
          // 构建格式化后的日期字符串
          var beginData = year + "-" + month + "-" + day;
          searchValue['beginData'] = beginData;
        }
        if (i==1){
          var endData = year + "-" + month + "-" + day;
          searchValue['endData'] = endData;
        };
      } //结束for，完成日期的拼接

      // 使用axios发送请求 获取license的申请数据
      try {
        const response = await this.$http.get("/api/CMC/workrecords/analysisselect?beginData="+searchValue['beginData']+"&endData="+searchValue['endData'])
        //this.templates= response.data.data;
        console.log('获得this.analysisData为',response.data.data);
        this.analysisData = response.data.data; // 这里不能将整个data赋过去，会造成其他数据被覆盖
        console.log('获得this.analysisData["annularChart_data"]为',this.analysisData["annularChart_data"]);
        this.analysisData['licenseData'][0]['省份']='申请单位数' // 字典里面插入 省份这个列
        //for循环计算license申请的 合计数
        let license_total = 0;
        for (const dict of this.analysisData['licenseData']) { // 遍历字典的键
          for (const value of Object.values(dict)) { // 遍历字典的值
            if (typeof value === 'number') { license_total += value; } // 如果是数字，则相加, 目的是为排除开汉字 申请单位数
          }
        }
        this.analysisData['licenseData'][0]['合计']=license_total //字典加入合计数

      } catch (error) {
        console.log(error);
        this.$message.error('错了哦，仔细看错误信息弹窗');
        alert("失败" + error);
      }
    
      //成功的消息提示
      this.$message({
        message: searchValue['beginData']+' 到 '+searchValue['endData']+' 查询成功',
        type: 'success'
       });
       //■请求get完成后，就将参数赋到setOption中，如果放到get外面则无效了 调整各个图形的对应参数
      //受理情况的柱形图 复制修改它的 xAxis 和 series
      let myChart = echarts.getInstanceByDom(document.getElementById("myChart")); // 获取到当前的myChart实例
      // console.log('this.analysisData的myChart_xAxis',this.analysisData['myChart_xAxis']);
      // 计算柱形图的数据总和
      let total = 0;
      for (var i = 0; i < this.analysisData['myChart_series'].length; i++) {
          total +=parseInt(this.analysisData['myChart_series'][i]);
      };
      
      console.log('总和',this.analysisData['myChart_series']);
      // 构造柱形图的 series 数据
      let seriesData = this.analysisData['myChart_series'].map(function(value) {
          let percentage = ((value / total) * 100).toFixed(2); // 计算百分比
          //弹出提示
          console.log('数值',value,total);
          return {
              value: value,
              label: { // 设置柱形图的数值
                  show: true,
                  position: 'top',
                  formatter: '{b}\n{c}次 ({d}%)'.replace('{d}', percentage),
              }
          };
      });
      // 使用构造好的 seriesData 绘制柱形图
      if (myChart){ // 修改xAxis的data参数
        myChart.setOption({
          xAxis: {data: this.analysisData['myChart_xAxis']},
          // series: {data: this.analysisData['myChart_series']}
          series: {data: seriesData}
      });
      }; //结束if判断

     //受理情况的饼状图 修改它的 data
     let annularChart = echarts.getInstanceByDom(document.getElementById("annularChart")); // 获取到当前的annularChart实例
     if (annularChart){ // 修改annularChart的data参数
        annularChart.setOption({
          series: {data: this.analysisData["annularChart_data"]}
      });
      }; //结束if判断

     // 计算描述内容上的各种合计数
     this.all_total = 0; // 初始化清零
     this.all_softbug =0 // 初始化清零
     this.all_sspz = 0;  // 初始化清零
     this.all_ycsjcl = 0;// 初始化清零
     for (var i = 0; i < this.analysisData['tableData'].length; i++) {
        this.all_total += parseInt(this.analysisData['tableData'][i].total);
        this.all_softbug += parseInt(this.analysisData['tableData'][i].softbug);
        this.all_sspz += parseInt(this.analysisData['tableData'][i].sspz);
        this.all_ycsjcl += parseInt(this.analysisData['tableData'][i].ycsjcl);
      }
     
     },
    // 结束 查询 事件
  },

};
</script>

<style>
/* 通过设置div class对应的float方向，可以让两个div在同一行 */
.myChart {float: left;}
.annularChart {float: left;}
</style>