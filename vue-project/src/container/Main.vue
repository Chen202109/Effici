<template>
	<el-container>
		<el-row :gutter="20">
		  <el-col :span="5">
			<div class="grid-content bg-purple" style='background-color: #7ECA2B'>
			<!-- 左侧菜单插入 -->
				<el-container>
				  <el-aside width="240px">
					<template>
						<router-view></router-view>
					</template>
				  </el-aside>
				  <el-container>
					<el-header>头部</el-header>
					<el-main>
					  <!-- <router-view></router-view> -->
					</el-main>
				  </el-container>
				</el-container>
			</div>
		  </el-col>
		</el-row>	 
	</el-container>
</template>

<script>
export default {
  data () {
    return {
      msg: 'Hello Vue!'
    }
  },
}

</script>

<style scoped>

</style>