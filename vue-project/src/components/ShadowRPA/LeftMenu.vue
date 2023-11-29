<template>
  <!-- el-menu 在加入 router 后，el-menu-item 中index="new"就会进行网页跳转 -->
  <div style="height: 100%;">
    <el-container style="height: 100%;">
      <el-aside style="width: 220px">
		    <!-- <el-menu :default-active="$route.path" class="el-menu-vertical-demo" router> -->
        <el-menu :default-active="$route.path" class="el-menu-vertical-demo">
          <el-submenu index="1">
            <template slot="title">
              <i class="el-icon-location"></i>
              <span>SaaS运营</span>
            </template>
            <el-menu-item-group>
              <el-menu-item index="new">受理明细</el-menu-item>
              <el-menu-item index="/navigatorTwo/index">数据汇报</el-menu-item>
              <el-menu-item index="/navigatorTherr/index">升级汇报</el-menu-item>
              <el-menu-item index="/navigatorFour/index">全国数据统计</el-menu-item>
            </el-menu-item-group>
          </el-submenu>
        </el-menu>
      </el-aside>
    </el-container>
  </div>
</template>
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
