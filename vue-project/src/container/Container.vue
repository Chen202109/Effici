<template>
<!-- 顶行头部 -->
<el-container>
  <el-header style="background-color: #545c64">
	<el-row type="flex" justify="center" align="middle">
		<el-col :span="5"><div class="grid-content bg-purple"></div></el-col>
		<el-col :span="14">
			<div class="grid-content bg-purple-light" style="background-color: #545c64">
				<template>
					<TopNavMenu></TopNavMenu>
				</template>
			</div>
		</el-col>
		<el-col :span="5"><div class="grid-content bg-purple"></div></el-col>
	</el-row>
  </el-header>
  
  <!-- 中间分两部分，左侧和main -->
    <el-main style='background-color: #45C0FF'>
		<template>
			<!-- <router-link to="/jira">Jira</router-link> -->
			<!-- <router-view/> -->
			<!-- <Main></Main> -->
			<router-view></router-view>
		</template>
	</el-main>
 
</el-container>
</template>

<script>
import Main from '@/container/Main.vue'
import TopNavMenu from '@/components/TopNavMenu'

export default {
  data () {
    return {
      msg: 'Hello Vue!'
    }
  },
  components: { Main,TopNavMenu }
}
</script>

<style scoped>
  .el-row {
	height: 100%;
    margin-bottom: 20px;
    &:last-child {
      margin-bottom: 0;
    }
  }
  .el-col {
    border-radius: 2px;
  }
  .bg-purple-dark {
	background: #99a9bf;
  }
  .bg-purple {
	background: #545c64;
  }
  .bg-purple-light {
    background: #545c64;
  }
  .grid-content {
    border-radius: 2px;
    min-height: 60px;
  }
  .row-bg {
    padding: 10px 0;
    background-color: #f9fafc;
  }
</style>