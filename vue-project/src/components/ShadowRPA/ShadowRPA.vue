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
        <el-tabs type="border-card" closable @tab-remove="removeTab" class="main-el-tab-pane">
          <el-tab-pane>
            <template>
              <AssistSubmit></AssistSubmit>
            </template>
          </el-tab-pane>

          <el-tab-pane label="数据汇报" overflow-y: auto class="main-el-tab-pane">
            <template>
              <AnalysisData></AnalysisData>
            </template>
          </el-tab-pane>

          <el-tab-pane label="升级汇报" overflow-y: auto>
            <template>
              <AnalysisUpgrade></AnalysisUpgrade>
            </template>
          </el-tab-pane>

          <el-tab-pane label="全国数据统计" overflow-y: auto>
            <template>
              <AnalysisCountryData></AnalysisCountryData>
            </template>
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
import AnalysisUpgrade from "@/components/ShadowRPA/AnalysisUpgrade.vue"
import AnalysisCountryData from "@/components/ShadowRPA/AnalysisCountryData.vue"

export default {
  data() {
    return {};
  },

  methods: {
    removeTab(targetName) {
      let tabs = this.editableTabs;
      let activeName = this.editableTabsValue;
      if (activeName === targetName) {
        tabs.forEach((tab, index) => {
          if (tab.name === targetName) {
            let nextTab = tabs[index + 1] || tabs[index - 1];
            if (nextTab) {
              activeName = nextTab.name;
            }
          }
        });
      }
      this.editableTabsValue = activeName;
      this.editableTabs = tabs.filter((tab) => tab.name !== targetName);
    },
  },

  components: { LeftMenu, AssistSubmit, AnalysisData, AnalysisUpgrade, AnalysisCountryData },
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
    padding-right: 10px;
}
</style>
