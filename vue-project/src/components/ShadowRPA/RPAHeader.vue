<template>
	<div>
		<el-page-header @back="goBack" content="填写内容">
		</el-page-header>
	</div>
</template>

<script>
  export default {
    methods: {
      goBack() {
        console.log('go back');
      }
    }
  }
</script>
<style scoped>

</style>