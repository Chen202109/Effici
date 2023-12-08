<template>
  <el-container>
    <!-- aside左侧 -->
    <el-aside style="width: 220px">
      <template>
        <LeftMenu></LeftMenu>
      </template>
    </el-aside>
    <!-- 主体右侧 -->
    <el-container>
      <!-- el-main自带padding上下左右20，为了和leftMenu平齐，所以将上下的padding消除 -->
      <el-main style="padding: 0 10px">
        <!-- 放入动态选项卡tagsView -->
        <el-tabs type="border-card" v-model="activeTab" @tab-remove="removeTab" @tab-click="tabClick" class="main-el-tab-pane">
          <el-tab-pane v-for="item in tabsItem" :key="item.name" :label="item.title" :name="item.name" :closable="item.closable" :ref="item.ref">
            <component :is="item.content"></component>
          </el-tab-pane>
        </el-tabs>
      </el-main>
    </el-container>
  </el-container>
</template>

<script>
import LeftMenu from "@/components/ShadowRPA/LeftMenu.vue"
import AssistSubmit from "@/components/ShadowRPA/AssistSubmit.vue"
import AnalysisData from "@/components/ShadowRPA/AnalysisData.vue"
import AnalysisUpgradeTrend from "@/components/ShadowRPA/AnalysisUpgradeTrend.vue"
import AnalysisCountryData from "@/components/ShadowRPA/AnalysisCountryData.vue"
import AnalysisMonitorProblem from "@/components/ShadowRPA/AnalysisMonitorProblem.vue"
import AnalysisPrivatizationLicense from "@/components/ShadowRPA/AnalysisPrivatizationLicense.vue"
import AnalysisLargeProblemData from "@/components/ShadowRPA/AnalysisLargeProblemData.vue"

export default {
  components: { LeftMenu, AssistSubmit, AnalysisData, AnalysisUpgradeTrend, 
    AnalysisCountryData, AnalysisMonitorProblem, AnalysisPrivatizationLicense, AnalysisLargeProblemData},

  data() {
    return {
      // 被激活的连接地址
      activePath: '',
      activeTab: '1', //默认显示的tab
      tabIndex: 1, //tab目前显示数
      tabsItem: [
        {
          title: '受理明细',
          name: '1',
          closable: false,
          ref: 'tabs',
          content: AssistSubmit
        }
      ],
      tabsPath: [
        {
          name: "1",
          path: '/AssistSubmit'
        }
      ]
  }

  },

  methods: {

    /**
     * 删除Tab
     * @param {*} targetName 
     */
    removeTab(targetName) { 
      let tabs = this.tabsItem; //当前显示的tab数组
      let activeName = this.activeTab; //点前活跃的tab

      //如果当前tab正活跃 被删除时执行
      if (activeName === targetName) {
        tabs.forEach((tab, index) => {
          if (tab.name === targetName) {
            let nextTab = tabs[index + 1] || tabs[index - 1];
            if (nextTab) {
                activeName = nextTab.name;
                this.tabClick(nextTab)
            }
          }
        });
      }
      this.activeTab = activeName;
      this.tabsItem = tabs.filter(tab => tab.name !== targetName);
      //在tabsPath中删除当前被删除tab的path
      this.tabsPath = this.tabsPath.filter(item => item.name !== targetName)
    },


   /**
    * 通过当前选中tabs的实例获得当前实例的path 重新定位路由
    * @param {*} thisTab 当前选中的tabs的实例
    */
    tabClick(thisTab) {
        
        let val = this.tabsPath.filter(item => thisTab.name == item.name)
        this.$router.push({
          path: val[0].path
        })
    }

  },

  watch: {
    '$route': function (to) {  //监听路由的变化，动态生成tabs
      let flag = true //判断是否需要新增页面
      const path = to.path
      if (Object.keys(to.meta).length != 0) {
        for (let i = 0; i < this.$refs.tabs.length; i++) {
          if (this.$refs.tabs[i].label == to.meta.title) {
            this.activeTab = this.$refs.tabs[i].name  //定位到已打开页面
            flag = false
            break
          }
        }
        //新增页面
        if (flag) {
          //获得路由元数据的name和组件名
          const thisName = to.meta.title
          const thisComp = to.meta.comp
          //对tabs的当前激活下标和tabs数量进行自加
          let newActiveIndex = ++this.tabIndex + ''
          //动态双向追加tabs
          this.tabsItem.push({
            title: thisName,
            name: String(newActiveIndex),
            closable: true,
            ref: 'tabs',
            content: thisComp
          })
          this.activeTab = newActiveIndex
          if (this.tabsPath.indexOf(path) == -1) {
            this.tabsPath.push({
              name: newActiveIndex,
              path: path
            })
          }
        }
      }
    }
  }

};
</script>


<style>
/* 加入使tab-pane可以固定高度或者出现滚动 */
/* calc()计算的意思，vh是指CSS中相对长度单位，表示相对视口高度（Viewport Height），1vh = 1% 乘 视口高度 */
/* calc()这里不能用100% */
/* 最后overflow-y: auto; 意思是 溢出时出现滚动条*/
.el-tab-pane {
  height: calc(100vh - 190px);
  overflow-y: auto;
}

.main-el-tab-pane{
    padding-right: 0px;
}
</style>
