<template>
  <!-- el-menu 在加入 router 后，el-menu-item 中index="new"就会进行网页跳转 -->
  <div>
    <el-container>
      <el-aside width="240px">
		<!-- <el-menu :default-active="$route.path" class="el-menu-vertical-demo" router> -->
        <el-menu :default-active="$route.path" class="el-menu-vertical-demo">
		
          <el-submenu index="1">
            <template slot="title">
              <i class="el-icon-location"></i>
              <span>折叠导航</span>
            </template>
            <el-menu-item-group>
              <el-menu-item index="new">管理信息</el-menu-item>
              <el-menu-item index="/navigatorTwo/index">个人设置</el-menu-item>
              <el-menu-item index="/navigatorTherr/index">插件管理</el-menu-item>
              <el-menu-item index="/navigatorFour/index">我的管理</el-menu-item>
            </el-menu-item-group>
          </el-submenu>
		  
		  <!-- el-menu-item后面加上 index="2" 就会跳转到该页面 -->
		  <el-menu-item>
			<i class="el-icon-menu"></i>
			<span slot="title">导航二</span>
		  </el-menu-item>
		  
        </el-menu>
      </el-aside>
    </el-container>
  </div>
</template>
<style scoped>
.el-header {
  background-color: #b3c0d1;
  color: #333;
  line-height: 60px;
  height: 100%;
}

.el-aside {
  background-color: #d3dce6;
  color: #333;
  height: 100vh;
}

.el-main {
  background-color: #e9eef3;
  color: #333;
}
</style>
