<template>
<!-- Menu 还提供了background-color、text-color和active-text-color，分别用于设置菜单的背景色、菜单的文字颜色和当前激活菜单的文字颜色 -->
<el-header>
	<el-menu :default-active="activeIndex" class="el-menu-demo" mode="horizontal" @select="handleSelect" background-color="#545c64"  text-color="#fff"  active-text-color="#ffd04b" router>
	  <el-menu-item index="/CMC/ShadowRPA">SaaS中心</el-menu-item>
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