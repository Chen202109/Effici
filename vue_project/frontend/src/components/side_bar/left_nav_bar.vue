<template>
    <el-row class="tac">
        <el-col :span="24">
            <el-menu
                default-active="2"
                class="el-menu-vertical-demo"
                @open="handleOpen"
                @close="handleClose"
                background-color="#545c64"
                text-color="#fff"
                active-text-color="#ffd04b"
                style="height: 100vh; font-size: 11px"
                @select="handleClick"
            >
                <h2>菜单栏</h2>

                <el-menu-item index="/user_management/index">
                    <i class="el-icon-user-solid"></i>
                    <span slot="title">用户管理</span>
                </el-menu-item>

                <el-menu-item index="/week_saas_work_analysis/index">
                    <i class="el-icon-s-data"></i>
                    <span slot="title">本周SaaS受理数据统计展示</span>
                </el-menu-item>

                <el-submenu index="3">
                    <template slot="title">
                        <i class="el-icon-notebook-1"></i>
                        <span>SaaS业务处理登记</span>
                    </template>
                    <el-menu-item index="/saas_work_records/week_saas_worksheet">本周SaaS受理工时统计表</el-menu-item>
                    <el-menu-item index="/saas_work_records/saas_upgrade_work">升级计划统计表</el-menu-item>
                </el-submenu>

                <el-submenu index="4">
                    <template slot="title">
                        <i class="el-icon-search"></i>
                        <span>SaaS受理数据查询</span>
                    </template>
                    <el-menu-item index="/saas_worksheet_data_search/saas_worksheet_data_search">SaaS受理工时统计表查询</el-menu-item>
                    <el-menu-item index="/saas_worksheet_data_search/saas_upgrade_work_data_search">升级计划统计表查询</el-menu-item>
                    <el-menu-item index="/saas_worksheet_data_search/saas_license_data_search">license发放表查询</el-menu-item>
                </el-submenu>

            </el-menu>
        </el-col>
    </el-row>
</template>

<style scope>
    /* .el-menu-item{
        padding-left: 10px !important;
    }

    .el-submenu .el-menu-item {
        padding-left: 40px !important;
    }  */
</style>
  
<script>
export default {
    name: "LeftNavBarComponent",
    methods: {
        handleOpen(key, keyPath) {
            console.log(key, keyPath);
        },
        handleClose(key, keyPath) {
            console.log(key, keyPath);
        },
        handleClick(index){
            this.$router.push({ path: index})
            this.loading = false
        }
    },
};
</script>