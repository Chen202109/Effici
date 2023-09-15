<template>
<!-- Menu 还提供了background-color、text-color和active-text-color，分别用于设置菜单的背景色、菜单的文字颜色和当前激活菜单的文字颜色 -->
<el-header>
	<el-menu :default-active="activeIndex" class="el-menu-demo" mode="horizontal" @select="handleSelect" background-color="#545c64"  text-color="#fff"  active-text-color="#ffd04b" router>
	  <el-menu-item index="/CMC/ShadowRPA">SaaS中心</el-menu-item>
	  <el-submenu index="2">
		<template slot="title">我的工作台</template>
		<el-menu-item >选项1</el-menu-item>
		<el-menu-item >选项2</el-menu-item>
		<el-menu-item >选项3</el-menu-item>
		<el-submenu index="2-4">
		  <template slot="title">选项4</template>
		  <el-menu-item >选项1</el-menu-item>
		  <el-menu-item >选项2</el-menu-item>
		  <el-menu-item >选项3</el-menu-item>
		</el-submenu>
	  </el-submenu>
	  <el-menu-item index="4" disabled>消息通知</el-menu-item>
	  <el-menu-item><a href="http://172.18.150.4:8080/CMC/login" target="_blank">重新登录</a></el-menu-item>
	</el-menu>
</el-header>
</template>

<script>
  export default {
    data() {
      return {
        activeIndex: '1',
        activeIndex2: '1'
      };
    },
    methods: {
      handleSelect(key, keyPath) {
        console.log(key, keyPath);
      }
    }
  }
</script>