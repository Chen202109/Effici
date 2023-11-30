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
import AssistSubmit from "@/components/ShadowRPA/AssistSubmit.vue"
import AnalysisData from "@/components/ShadowRPA/AnalysisData.vue"
import AnalysisUpgrade from "@/components/ShadowRPA/AnalysisUpgrade.vue"
import AnalysisCountryData from "@/components/ShadowRPA/AnalysisCountryData.vue"
import AnalysisThirdPartyProblem from "@/components/ShadowRPA/AnalysisThirdPartyProblem.vue"

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
		    { 
          path: '/CMC/ShadowRPA', 
          name: '流程自动化', 
          component: ShadowRPA,
          children: [
            { path: '/AssistSubmit', component: AssistSubmit, meta: {keepAlive: true, comp: AssistSubmit, name: 'AssistSubmit', title:"受理明细"}},
            { path: '/AnalysisData', component: AnalysisData, meta: {keepAlive: true, comp: AnalysisData, name: 'AnalysisData', title:"数据汇报"}},
            { path: '/AnalysisUpgrade', component: AnalysisUpgrade, meta: {keepAlive: true, comp: AnalysisUpgrade, name: 'AnalysisUpgrade', title:"升级汇报"}},
            { path: '/AnalysisCountryData', component: AnalysisCountryData, meta: {keepAlive: true, comp: AnalysisCountryData, name: 'AnalysisCountryData', title:"全国数据统计"}},
            { path: '/AnalysisThirdPartyProblem', component: AnalysisThirdPartyProblem, meta: {keepAlive: true, comp: AnalysisThirdPartyProblem, name: 'AnalysisThirdPartyProblem', title:"生产监控异常统计"}}
          ]
        },
        { path: '/CMC/ew', name: '新页面', component: New, },
        { path: '/CMC/dashboard', name: 'router首页', component: Dashboard, },
        { path: '/CMC/article', name: 'router文章', component: Article, },
        { path: '/CMC/jira', name: '速记BUG', component: Jira, },
      ]
    },
  ]
})