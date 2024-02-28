import Vue from 'vue'
import App from './App'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import http from 'axios'
import '@/styles/index.scss'
import * as echarts from 'echarts'

import router from './router'


Vue.use(ElementUI)
Vue.prototype.$http = http
Vue.prototype.HOST = '/api'
//将ECharts绑定在vue的原型
Vue.prototype.$echarts = echarts 

Vue.config.productionTip = false


new Vue({
  el: '#app',
  router,
  render: h => h(App)
})

// 导航守卫限制路由跳转
//router.beforeEach((to, from, next) => {
//	if (!to.meta.needLogin && !localStorage.token){
//		return next('/login')
//	}
//	next()
//})

//router.beforeEach(function (to, from, next){
//  if(to.path === '/login'){
//    sessionStorage.removeItem('user');
//  }
//  var user = sessionStorage.getItem('user');
//  //console.log(user);
//  if(!user && to.path !== '/login'){
//	//未登录
//    //next可以传递一个路由对象作为参数 表示需要跳转到的页面
//    next({
//      path: '/login'
//    })
//  }else{
//    next(); //继续往后走
//  }
//})