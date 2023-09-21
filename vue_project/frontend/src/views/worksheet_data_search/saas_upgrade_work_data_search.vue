<template>
    <div>
        <el-container style="height: 100vh;">
                <el-header style="text-align: right; font-size: 12px" >
                    <el-dropdown>
                        <i
                            class="el-icon-setting"
                            style="margin-right: 15px"
                        ></i>
                        <el-dropdown-menu slot="dropdown">
                            <el-dropdown-item>查看</el-dropdown-item>
                            <el-dropdown-item>新增</el-dropdown-item>
                            <el-dropdown-item>删除</el-dropdown-item>
                        </el-dropdown-menu>
                    </el-dropdown>
                    <span>GGBond</span>
                </el-header>

                <el-main>
                    <el-table :data="tableData">
                        <el-table-column prop="date" label="日期" width="140">
                        </el-table-column>
                        <el-table-column prop="name" label="姓名" width="120">
                        </el-table-column>
                        <el-table-column prop="address" label="地址">
                        </el-table-column>
                    </el-table>
                </el-main>

                <el-footer>Footer</el-footer>
            </el-container>
    </div>
</template>
  
<style>
.el-header, .el-footer {
    background-color: #b3c0d1;
    color: #333;
    line-height: 60px;
}

.el-aside {
    color: #333;
}
</style>
  
<script>
export default {
    name: "SaasUpgradeWorkDataSearch",
    data() {
        const item = {
            date: "2016-05-02",
            name: "GGBond",
            address: "上海市普陀区金沙江路 1518 弄",
        };
        return {
            tableData: Array(4).fill(item),
        };
    },
};
</script>