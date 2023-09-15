<template>
  <div class="component-wrapper">
    <search v-on:search="onSearch"></search>
    <add-form v-if="showForm" v-on:submit="onSubmit"></add-form>
    <el-button type="primary" class="add-button" icon="el-icon-plus" @click="showForm = true">新增表单</el-button>
    <table :table-data="tableData"></table>
  </div>
</template>

<script>
import search from '@/components/ShadowRPA/AssistSubmit_search.vue'
import addForm from '@/components/ShadowRPA/AssistSubmit_addForm.vue'
import table from '@/components/ShadowRPA/AssistSubmit_table.vue'

export default {
  components: {
    search,
    addForm,
    table
  },
  data() {
    return {
      showForm: false,
      tableData: [
        {
          state: '已解决',
          date: '2023-04-25',
          region: '北京',
          description: '服务器连接不上',
          solution: '检查网络连接是否正常'
        },
        {
          state: '进行中',
          date: '2023-04-24',
          region: '上海',
          description: '数据丢失',
          solution: '正在调查'
        },
      ]
    }
  },
  methods: {
    onSearch(filter) {
      // 根据筛选条件筛选数据并渲染表格
      // ...
      this.tableData = filteredData
    },
    onSubmit(form) {
      // 将表单数据保存到数据库
      // ...
      this.showForm = false
      this.$message({
        message: '添加成功',
        type: 'success'
      })
    }
  }
}
</script>

<style scoped>
.component-wrapper {
  padding: 20px;
}
.add-button {
  margin-bottom: 20px;
}
</style>