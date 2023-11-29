<template>
    <el-container>
      
      <el-container :style="{height: setHeight+'px'}">

        <el-aside style="width: auto">
          <el-menu :default-active="String(activeNav)" router class="el-menu-vertical-demo" :collapse="isCollapse">
            <el-submenu index="1">
              <template slot="title">
                <span slot="title">基础设置</span>
              </template>
              <el-menu-item index="/nav">导航</el-menu-item>
              <el-menu-item index="/mineInfo">个人信息</el-menu-item>
            </el-submenu>
            <el-submenu index="2">
              <template slot="title">
                <i class="fa fa-book"></i>
                <span slot="title">文章管理</span>
              </template>
              <el-menu-item index="/fuillEditor">fuillEditor</el-menu-item>
              <el-menu-item index="/category">分类管理</el-menu-item>
            </el-submenu>
          </el-menu>
        </el-aside>

        <el-main :style="{height: setHeight+'px', padding: 0}">
          <el-tabs v-model="activeTab" type="card" @tab-remove="removeTab" @tab-click="tabClick">
            <el-tab-pane v-for="(item) in tabsItem"
                         :key="item.name"
                         :label="item.title"
                         :name="item.name"
                         :closable="item.closable"
                         :ref="item.ref">
              <component :is="item.content"></component>
            </el-tab-pane>
          </el-tabs>
        </el-main>
      </el-container>
    </el-container>
  </template>
  
  <script>
    import welcome from '../views/Welcome'
    import setNav from '../views/SetNav'
    import mineInfo from '../views/MineInfo'
    import fuillEditor from "../views/FuillEditor";
    import category from "../views/Category";
  
    export default {
      name: "Home",
      data() {
        return {
          isCollapse: false,  //false为展开 true为收缩
          activeTab: '1', //默认显示的tab
          tabIndex: 1, //tab目前显示数
          tabsItem: [
            {
              title: '首页',
              name: '1',
              closable: false,
              ref: 'tabs',
              content: welcome
            }
          ],
          tabsPath: [{
            name: "1",
            path: '/welcome'
          }]
        }
      },
      computed: {
        setHeight() {
          return document.documentElement.clientHeight - 65
        },
        activeNav() { //当前激活的导航
          return this.$route.path
        }
      },
      watch: {
        '$route': function (to) {  //监听路由的变化，动态生成tabs
          let flag = true //判断是否需要新增页面
          const path = to.path
          if (Object.keys(to.meta).length != 0) {
            for (let i = 0; i < this.$refs.tabs.length; i++) {
              if (i != 0) { //首页不判断 如果页面已存在，则直接定位当页面，否则新增tab页面
                if (this.$refs.tabs[i].label == to.meta.name) {
                  this.activeTab = this.$refs.tabs[i].name  //定位到已打开页面
                  flag = false
                  break
                }
              }
            }
            //新增页面
            if (flag) {
              //获得路由元数据的name和组件名
              const thisName = to.meta.name
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
              /*
              * 当添加tabs的时候，把当前tabs的name作为key，path作为value存入tabsPath数组中
              * key:tabs的name
              * value:tabs的path
              * {
              *   key: name,
              *   value: path
              * }
              * ///后面需要得到当前tabs的时候可以通过当前tabs的name获得path
              * */
              if (this.tabsPath.indexOf(path) == -1) {
                this.tabsPath.push({
                  name: newActiveIndex,
                  path: path
                })
              }
            }
          }
        }
      },
      methods: {
        isOpen() { //判断左侧栏是否展开或收缩
          if (this.isCollapse == false) {
            this.isCollapse = true
          } else {
            this.isCollapse = false
          }
        },
        
        removeTab(targetName) { //删除Tab
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

      components: {
        welcome,
        setNav,
        mineInfo,
        fuillEditor,
        category
      }
    }
  </script>
  
  <style scoped>
    @import "~font-awesome/css/font-awesome.min.css";
  
    .el-menu-vertical-demo:not(.el-menu--collapse) {
      width: 200px;
      min-height: 400px;
      height: 100%;
    }
  
    .el-menu--collapse {
      height: 100%;
    }
  
    .el-header {
      background-color: #B3C0D1;
      color: #333;
      line-height: 60px;
    }
  
    .el-aside {
      color: #333;
    }
  
    .el-submenu [class^=fa] {
      vertical-align: middle;
      margin-right: 5px;
      width: 24px;
      text-align: center;
      font-size: 16px;
    }
  
  </style>
 