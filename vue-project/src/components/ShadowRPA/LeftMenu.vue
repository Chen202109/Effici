<template>
  <!-- el-menu 在加入 router 后，el-menu-item 中index="new"就会进行网页跳转 -->
  <div style="height: 100%;">
    <el-container style="height: 100%;">
      <el-aside style="width: 220px">
		    <!-- <el-menu :default-active="$route.path" class="el-menu-vertical-demo" router> -->
        <el-menu :default-active="$route.path" router class="el-menu-vertical-demo">
          <el-submenu index="1">
            <template slot="title">
              <i class="el-icon-location"></i>
              <span>SaaS运营</span>
            </template>
            <el-menu-item-group>
              <el-menu-item index="/AnalysisCountryData">全国数据统计</el-menu-item>
              <el-menu-item index="/AssistSubmit">受理明细</el-menu-item>
              <el-menu-item index="/AnalysisData">工单受理数据分析</el-menu-item>
              <el-menu-item index="/AnalysisUpgradeTrend">公有云升级汇报</el-menu-item>
              <el-menu-item index="/AnalysisLargeProblemData">私有化重大故障统计</el-menu-item>
              <el-menu-item index="/AnalysisMonitorProblem">生产监控异常统计</el-menu-item>
              <el-menu-item index="/AnalysisAddedServiceData">增值服务开通统计</el-menu-item>
              <el-menu-item index="/AnalysisPrivatizationLicense">v4 license受理数据统计</el-menu-item>
            </el-menu-item-group>
          </el-submenu>
        </el-menu>
      </el-aside>
    </el-container>
  </div>
</template>


<script>
  export default {
    computed: {
    /**
     * 当前激活的导航
     */
    activeNav() { 
      return this.$route.path
    }
  },
  }

</script>

<style scoped>
.el-header {
  background-color: #d3dce6;
  color: #333;
  line-height: 60px;
  height: 100%;
}

.el-aside {
  background-color: #FFF;
  color: #333;
}

.el-menu-item {
  background-color: #F8F5F4;
}

</style>
