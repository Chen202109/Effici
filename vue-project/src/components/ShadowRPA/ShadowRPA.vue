<template>
  <el-container>
    <!-- aside左侧 -->
    <el-aside width="200px">
      <template>
        <LeftMenu></LeftMenu>
      </template>
    </el-aside>
    <!-- 主体右侧 -->
    <el-container>
      <!-- 可以添加  style='height: 30px;' 来控制高度，默认60-->
      <el-header style="height: 5px">
        <template>
          <RPAHeader></RPAHeader>
        </template>
      </el-header>

      <el-main>
        <!-- 放入动态选项卡tagsView -->
        <el-tabs type="border-card" closable @tab-remove="removeTab">
          <el-tab-pane>
            <span slot="label"><i class="el-icon-date"></i>受理明细</span>
            <template>
              <AssistSubmit></AssistSubmit>
              <!-- 放入Pagination 分页组件 -->
              <div class="block" align="right">
                <span class="demonstration">分页的效果</span>
                <el-pagination background layout="prev, pager, next" :total="500"> </el-pagination>
              </div>
            </template>
          </el-tab-pane>

          <el-tab-pane label="数据汇报" overflow-y: auto>
            <template>
              <AnalysisData></AnalysisData>
            </template>
          </el-tab-pane>
        </el-tabs>
      </el-main>
    </el-container>
  </el-container>
</template>

<script>
import LeftMenu from "@/components/ShadowRPA/LeftMenu.vue"
import RPAHeader from "@/components/ShadowRPA/RPAHeader.vue"
import AssistSubmit from "@/components/ShadowRPA/AssistSubmit.vue"
import AnalysisData from "@/components/ShadowRPA/AnalysisData.vue"

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

  components: { LeftMenu, RPAHeader, AssistSubmit,AnalysisData },
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
</style>
