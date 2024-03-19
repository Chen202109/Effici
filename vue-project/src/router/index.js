import Vue from 'vue'
import Router from 'vue-router'
import Login from '@/views/Login/login'

import Dashboard from '@/views/temp/dashboard'
import Article from '@/views/temp/article'
import Jira from '@/views/temp/jira'
import New from '@/views/temp/new'

import Container from '@/container/Container'
import Main from '@/container/Main'
import ShadowRPA from '@/container/ShadowRPA.vue'

import SaaSDataDict from '@/views/saasCenter/SystemManagement/SaaSDataDict.vue'

import AssistSubmit from "@/views/saasCenter/WorkRecord/WorkRecord/AssistSubmit.vue"
import AnalysisData from "@/views/saasCenter/Industry/WorkRecordReport/AnalysisData.vue"
import AnalysisDataNew from "@/views/saasCenter/Industry/WorkRecordReport/AnalysisDataNew.vue"
import AnalysisUpgradeTrend from "@/views/saasCenter/Upgrade/AnalysisUpgradeTrend.vue"
import AnalysisCountryData from "@/views/saasCenter/WorkRecord/WorkRecordSummary/AnalysisCountryData.vue"
import AnalysisMonitorProblem from "@/views/saasCenter/Industry/Monitor/AnalysisMonitorProblem.vue"
import AnalysisAddedServiceData from "@/views/saasCenter/Industry/OrderedService/AnalysisAddedServiceData.vue"
import AnalysisPrivatizationLicense from "@/views/saasCenter/Industry/License/AnalysisPrivatizationLicense.vue"
import AnalysisLargeProblemData from "@/views/saasCenter/Industry/PrivatizationLargeProblem/AnalysisLargeProblemData.vue"

import TicketFolderAnalysisData from "@/views/saasCenter/TicketFolder/WorkRecordReport/AnalysisData.vue"
import TicketFolderAnalysisCountryData from "@/views/saasCenter/TicketFolder/WorkRecordSummary/AnalysisCountryData.vue"
import TicketFolderCustomerServiceRobot from "@/views/saasCenter/TicketFolder/CustomerServiceRobot/AnalysisRobot.vue"

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
            { path: '/AnalysisData', component: AnalysisData, meta: {keepAlive: true, comp: AnalysisData, name: 'AnalysisData', title:"行业工单受理数据分析"}},
            { path: '/AnalysisDataNew', component: AnalysisDataNew, meta: {keepAlive: true, comp: AnalysisDataNew, name: 'AnalysisDataNew', title:"行业工单受理数据分析（新）"}},
            { path: '/AnalysisUpgradeTrend', component: AnalysisUpgradeTrend, meta: {keepAlive: true, comp: AnalysisUpgradeTrend, name: 'AnalysisUpgrade', title:"行业公有云升级汇报"}},
            { path: '/AnalysisCountryData', component: AnalysisCountryData, meta: {keepAlive: true, comp: AnalysisCountryData, name: 'AnalysisCountryData', title:"全国数据统计"}},
            { path: '/AnalysisLargeProblemData', component: AnalysisLargeProblemData, meta: {keepAlive: true, comp: AnalysisLargeProblemData, name: 'AnalysisLargeProblemData', title:"V4私有化重大故障统计"}},
            { path: '/AnalysisMonitorProblem', component: AnalysisMonitorProblem, meta: {keepAlive: true, comp: AnalysisMonitorProblem, name: 'AnalysisMonitorProblem', title:"生产监控异常统计"}},
            { path: '/AnalysisAddedServiceData', component: AnalysisAddedServiceData, meta: {keepAlive: true, comp: AnalysisAddedServiceData, name: 'AnalysisAddedServiceData', title:"V4增值服务开通统计"}},
            { path: '/AnalysisPrivatizationLicense', component: AnalysisPrivatizationLicense, meta: {keepAlive: true, comp: AnalysisPrivatizationLicense, name: 'AnalysisPrivatizationLicense', title:"v4 license受理数据统计"}},
            { path: '/saasDataDict', component: SaaSDataDict, meta: {keepAlive: true, comp: SaaSDataDict, name: 'SaaSDataDict', title:"数据字典"}},

            { path: '/TicketFolderAnalysisData', component: TicketFolderAnalysisData, meta: {keepAlive: true, comp: TicketFolderAnalysisData, name: 'TicketFolderAnalysisData', title:"电子票夹受理数据分析"}},
            { path: '/TicketFolderAnalysisCountryData', component: TicketFolderAnalysisCountryData, meta: {keepAlive: true, comp: TicketFolderAnalysisCountryData, name: 'TicketFolderAnalysisCountryData', title:"电子票夹省份数据统计"}},
            { path: '/TicketFolderCustomerServiceRobot', component: TicketFolderCustomerServiceRobot, meta: {keepAlive: true, comp: TicketFolderCustomerServiceRobot, name: 'TicketFolderCustomerServiceRobot', title:"票夹智能客服数据统计"}}

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