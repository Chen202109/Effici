<template>
    <div>
        <el-container>
            <el-aside>
                <template>
                    <LeftNavBarComponent></LeftNavBarComponent>
                </template>
            </el-aside>
            <el-container style="height: 100vh;">
                <el-header style="text-align: right; font-size: 12px" >
                    <el-dropdown>
                        <i
                            class="el-icon-setting"
                            style="margin-right: 15px"
                        ></i>
                        <el-dropdown-menu slot="dropdown">
                            <el-dropdown-item>退出登录</el-dropdown-item>
                        </el-dropdown-menu>
                    </el-dropdown>
                    <span>GGBond</span>
                    
                </el-header>

                <el-main>
                    <router-view></router-view>
                </el-main>
            </el-container>
            
        </el-container>
    </div>
</template>
  
<style>
.el-header{
    background-color: #b3c0d1;
    color: #333;
    line-height: 60px;
}

.el-aside {
    color: #333;
}
</style>
  
<script>
import LeftNavBarComponent from '@/components/side_bar/left_nav_bar.vue';
// import SidebarItem from '@/layout/component/Sidebar/SidebarItem.vue'

export default {
    components: { LeftNavBarComponent },
    name: "LayoutComponent",
    data() {
    },
};
</script>