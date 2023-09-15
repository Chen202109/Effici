<template>
  <div class="login_container">
    <div class="login_box">
      <div class="avatar_box">
        <img src="../assets/bg01.jpg" alt="">
      </div>
      <el-form label-width="0px" class="login_in" ref="loginForm" :model="loginForm"  >
        <el-form-item prop="username">
          <el-input type="text" prefix-icon="el-icon-user" v-model="loginForm.userName"></el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input type="password" prefix-icon="el-icon-thumb" v-model="loginForm.passWord"></el-input>
        </el-form-item>
        <el-form-item class="btns">
          <el-button type="primary">登录</el-button>
          <el-button>重置</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script>
    export default {
        name: "Login",  
        data(){
            return {
                loginForm:{
                    userName:'admin',
                    passWord:'123456'
                }
            }
        }
    }
</script>

<style>
  .login_container {
    background-color: #42b983;
    height: 100%;
  }

  .login_box {
    width: 450px;
    height: 300px;
    background-color: #fff;
    border-radius: 3px;
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);

    .avatar_box {
      height: 130px;
      width: 130px;
      border: 1px solid #eee;
      border-radius: 50%;
      box-shadow: 0 0 10px #ddd;
      position: absolute;
      left: 50%;
      transform: translate(-50%, -50%);
      background-color: #fff;
      padding: 10px;
      img {
        width: 100%;
        height: 100%;
        border-radius: 50%;
        background-color: #eee;
      }
    }
  }

  .btns {
    display: flex;
    justify-content: flex-end;

  }

  .login_in {
    position: absolute;
    bottom: 0;
    width: 100%;
    padding: 0 20px;
    box-sizing: border-box;
  }
</style>