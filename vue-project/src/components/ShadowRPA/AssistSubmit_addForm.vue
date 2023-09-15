<template>
  <div>
    <hr>
    <el-form :model="form" label-width="120px">
      <el-form-item label="登记日期">
        <el-date-picker v-model="form.date" type="date"></el-date-picker>
      </el-form-item>
      <el-form-item label="产品类型">
        <el-select v-model="form.region" placeholder="请选择">
          <el-option v-for="(item, index) in regionOptions" :key="index" :label="item.label" :value="item.value"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="问题描述">
        <el-input type="textarea" v-model="form.description"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitForm">提交</el-button>
        <el-button @click="resetForm">重置</el-button>
      </el-form-item>
    </el-form>
    <hr>
  </div>
</template>

<script>
export default {
  data() {
    return {
      form: {
        date: new Date,
        region: '',
        description: ''
      },
      regionOptions: [{
        value: 'yiliao',
        label: '医疗'
      }, {
        value: 'gaoxiao',
        label: '高校'
      },{
        value: 'tongyong',
        label: '通用'
      },]
    }
  },
  methods: {
    submitForm() {
      // 触发提交事件，将表单数据传给父组件
      this.$emit('submit', this.form)
    },
    resetForm() {
      // 重置表单数据
      this.form.date = ''
      this.form.region = ''
      this.form.description = ''
    }
  }
}
</script>