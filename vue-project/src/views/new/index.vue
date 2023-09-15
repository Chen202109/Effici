<template>
  <el-row :gutter="20">
    <el-col :span="8" >
        <div class="grid-content bg-purple-left">
        <testComponent></testComponent>
        </div>
    </el-col>
    <el-col :span="10"><div class="grid-content bg-purple"></div></el-col>
    <el-col :span="6"><div class="grid-content bg-purple-right"></div></el-col>
  </el-row>
</template>

<script>
//1.先使用import导入你要在该组件中使用的子组件
import testComponent from "./testComponent.vue";
export default {
  //2.然后,在components中写入子组件
  components: { testComponent },
  methods: {},
};
</script>

<style>
.el-row {
  margin-bottom: 20px;
}
.el-col {
  border-radius: 4px;
}
.bg-purple-left {
  background: #ffffff;
}
.bg-purple {
  background: #d3dce6;
}
.bg-purple-right {
  background: #e5e9f2;
}
.grid-content {
  border-radius: 4px;
  min-height: 36px;
}
.row-bg {
  padding: 10px 0;
  background-color: #0657f8;
}
</style>