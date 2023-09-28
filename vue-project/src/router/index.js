import Vue from 'vue'
import Router from 'vue-router'
import Login from '@/views/login'
import New from '@/views/new'
import Container from '@/container/Container'
import Main from '@/container/Main'
import Dashboard from '@/views/dashboard'
import Article from '@/views/article'
import Jira from '@/views/jira'

import ShadowRPA from '@/components/ShadowRPA/ShadowRPA.vue'

Vue.use(Router)

export default new Router({
	routes: [
    {
      path: '/CMC/login',
      name: 'Login',
      component: Login 
    },
    {
      path: '/',
      redirect: '/CMC/login', 
      name: 'Container',
      component: Container, /* 使用component配置的组件Container, 进入的时候重定向到 redirect配置的 '/login' 地址 */
	  meta:{ needLogin:true},
      children: [
	    { path: '/CMC/main', name: '主页面', component: Main, },
		  { path: '/CMC/ShadowRPA', name: '流程自动化', component: ShadowRPA, },
        { path: '/CMC/ew', name: '新页面', component: New, },
        { path: '/CMC/dashboard', name: 'router首页', component: Dashboard, },
        { path: '/CMC/article', name: 'router文章', component: Article, },
        { path: '/CMC/jira', name: '速记BUG', component: Jira, },
      ]
    },
/*     {
      path: '/main',
      name: 'Main',
      component: Main
    }, */
  ]
})