
<template>
    <div style="height: 99%;">
        <el-container  style="height: 100%;">
            <el-aside style="height: 100%; width: 250px; border: 1px solid #d7d7d7;">
                <div class="tree-title">
                    数据字典类型
                    <div style="float: right;">
                        <el-link icon="el-icon-document-add" @click="showAddDataDictDialogModal">新增</el-link>
                    </div>
                </div>

                <el-input placeholder="输入关键字进行过滤" v-model="filterText" style="padding: 1px;"></el-input>

                <el-tree class="filter-tree" :data="dataDictList" :props="defaultProps" default-expand-all :filter-node-method="filterNode" accordion @node-click="handleNodeClick" ref="tree">
                    <span slot-scope="{ node, data }" class="slot-t-node">
                        <template>
                            <i class="el-icon-document"/>
                            <span>{{ node.label }}</span>
                        </template>
                    </span>
                </el-tree>
            </el-aside>
  
            <el-main>
                <div class="tree-title">
                    数据字典项目列表
                    <div style="float: right;">
                        <el-link icon="el-icon-document-add" @click="showAddDataDictDetailDialogModal">新增</el-link>
                    </div>
                </div>
                <el-table :data="currentDataDictDetail" border >
                    <el-table-column prop="level" label="层级编码" width="120">
                    </el-table-column>
                    <el-table-column prop="code" label="字典项编码" width="140">
                    </el-table-column>
                    <el-table-column prop="parentCode" label="父节点编码" width="120">
                    </el-table-column>
                    <el-table-column prop="name" label="字典项名称">
                    </el-table-column>
                    <el-table-column prop="enable" label="是否启用" width="120">
                    </el-table-column>
                </el-table>
            </el-main>
        </el-container>

        <div>
            <el-dialog class="smallSizeDialog" :title=this.addDataDictDialogTitle :visible.sync="showAddDataDictDialog" v-if="showAddDataDictDialog"
            :close-on-click-modal="false" width="30%" label-width="150px">
                <el-form :model="addDataDictForm" :rules="addDataDictFormRules" ref="addDataDictForm">
                    <el-form-item label="新增字典名称" prop="name">
                        <el-input v-model="addDataDictForm.name" autocomplete="off"></el-input>
                    </el-form-item>
                </el-form>
                <div slot="footer" class="dialog-footer" style="text-align: center;">
                    <el-button type="primary" @click="addDataDict">确 定</el-button>
                    <el-button @click="showAddDataDictDialog = false">取 消</el-button>
                </div>
            </el-dialog>
        </div>

        <div>
            <el-dialog class="smallSizeDialog" :title=this.addDataDictDetailDialogTitle :visible.sync="showAddDataDictDetailDialog" v-if="showAddDataDictDetailDialog"
            :close-on-click-modal="false" width="30%">
                <el-form :model="addDataDictDetailForm" label-width="120px" :rules="addDataDictDetailFormRules" ref="addDataDictDetailForm">
                    <el-form-item label="字典项目标签" prop="fullLabel" ref="addDataDictDetailFormFullLabel">
                        <el-input v-model="addDataDictDetailForm.fullLabel" autocomplete="off"></el-input>
                    </el-form-item>
                    <el-form-item label="字典项目系统" prop="systemLabel" ref="addDataDictDetailFormSystemLabel">
                        <el-input v-model="addDataDictDetailForm.systemLabel" autocomplete="off" placeholder="1代表行业, 2代表票夹, 为出错功能字典辨识"></el-input>
                    </el-form-item>
                    <el-form-item label="字典项目层级" prop="level" ref="addDataDictDetailFormLevel">
                        <el-input v-model="addDataDictDetailForm.level" autocomplete="off"></el-input>
                    </el-form-item>
                    <el-form-item label="字典父节点编码" prop="parentCode" ref="addDataDictDetailFormparentCode">
                        <el-input v-model="addDataDictDetailForm.parentCode" autocomplete="off"></el-input>
                    </el-form-item>
                    <el-form-item label="字典项目名称" prop="name" ref="addDataDictDetailFormName">
                        <el-input v-model="addDataDictDetailForm.name" autocomplete="off"></el-input>
                    </el-form-item>
                </el-form>
                <div slot="footer" class="dialog-footer" style="text-align: center;">
                    <el-button type="primary" @click="addDataDictDetail">确 定</el-button>
                    <el-button @click="closeAddDataDictDetailDialogModal">取 消</el-button>
                </div>
            </el-dialog>
        </div>

    </div>
</template>
  
<script>

export default {
    name: "SaaSDataDict",

    data() {
        // 校验字典项目添加form的validator
        var validateLabel = (rule, value, callback) => {
            // 想要实现的效果: 如果完整标签填写，则其他表单内容不需要填写，如果完整标签未填写，则需要填写想要加入的那个节点的层级，名称，父节点信息。
            if (this.addDataDictDetailForm.fullLabel == "" && (this.addDataDictDetailForm.level =="" && this.addDataDictDetailForm.name=="")) {
                callback(new Error("请填写项目完整标签或填写节点的具体层级，名字等信息"))
            } else {
                if (this.addDataDictDetailForm.fullLabel != "") {
                    //如果是full label填写了，则直接通过
                    callback()
                }else {
                    // 如果是节点的具体层级，名字等信息填写了，进一步判断
                    if (this.addDataDictDetailForm.level == "" || this.addDataDictDetailForm.name=="") {
                        // 如果其中有一个是空的，则不通过
                        callback(new Error("请填写完整标签或填写节点的具体层级，名字等信息"))
                    }
                    // 如果层级填写了大于1，但是没填写父节点信息，不通过
                    if ( this.addDataDictDetailForm.level > 1 && this.addDataDictDetailForm.parentCode==""){
                        callback(new Error("请填写对应层级的父节点的名称信息"))
                    }
                    // 都符合条件的，通过
                    callback()
                }                
            }
        }

        return {
            // 数据字典的标题的搜索filter
            filterText: '',
            // 数据字典在el-tree中的标识list
            dataDictList: [],
            // 当前所选中的数据字典
            currentDataDictCode:'',
            // 当前所选中的数据字典的数据
            currentDataDictDetail: [],
            defaultProps: {
                children: 'children',
                label: 'label'
            },

            // 新增数据字典相关data
            addDataDictDialogTitle: '新增数据字典',
            showAddDataDictDialog: false,
            addDataDictForm: {
                name: ''
            },
            addDataDictFormRules: {
                name: [
                    { required: true, message: '请输入新增数据字典名称', trigger: 'blur' }
                ],
            },

            // 新增数据字典条目相关data
            addDataDictDetailDialogTitle: '新增数据字典条目',
            showAddDataDictDetailDialog: false,
            addDataDictDetailForm: {
                fullLabel: '', //添加整个层级时候使用的
                systemLabel: '', //标识系统是哪个。1代表行业，2代表票夹。
                level: '', //添加单个层级时候使用，该单项的层级
                parentCode: '', //添加单个层级时候使用，该单项的父级节点名称
                name: '', //添加单个层级时候使用，该单项的名称
            },
            addDataDictDetailFormRules: {
                fullLabel: [
                    { required: true, message: '请输入新增数据字典项目完整标签', trigger: 'blur', validator: validateLabel }
                ],
                level: [
                    { required: true, message: '请输入新增数据字典项目层级', trigger: 'blur', validator: validateLabel}
                ],
                parentCode: [
                    // { required: true, message: '请输入新增数据字典项目父节点层级', trigger: 'blur', validator: validateLabel }
                ],
                name: [
                    { required: true, message: '请输入新增数据字典项目层级', trigger: 'blur', validator: validateLabel}
                ],
                systemLabel:[],
            },
        };
    },

    watch: {
        filterText(val) {
            this.$refs.tree.filter(val);
        }
    },

    mounted() {
        this.init();
    },

    methods: {

        /**
         * 页面的初始化，请求所有数据字典的名称list，然后请求第一个数据字典的数据
         */
        init() {
            this.$http.get(
                '/api/CMC/workrecords/system/data_dict_management_init'
            ).then(response => {
                if (response.status === 200) {
                    this.dataDictList = []
                    for (let i = 0; i < response.data.dataDictList.length; i++) {
                        this.dataDictList.push({
                            id: i + 1,
                            label: response.data.dataDictList[i]["dictCode"] + "-" + response.data.dataDictList[i]["name"]
                        })
                    }
                    console.log("now, the data dict list is: ", this.dataDictList)
                    if (response.data.dataDictList.length > 0) {
                        this.currentDataDictCode = response.data.dataDictList[0]["dictCode"]
                    }
                    this.currentDataDictDetail = response.data.dataDictFirst
                    console.log("now, the current data dict detail is: ", this.currentDataDictDetail)

                } else {
                    console.log(response.data.message)
                    this.$message.error(response.data.message)
                }
            }).catch((error) => {
                console.log(error.response.data.message)
                this.$message.error(error.response.data.message)
            })
        },

        /**
         * 树状组件过滤里面的node的label，找到模糊匹配的node
         * @param {*} value 
         * @param {*} data 
         */
        filterNode(value, data) {
            if (!value) return true;
            return data.label.indexOf(value) !== -1;
        },
        
        /**
         * 树状结构组件里的node被点击触发的事件，向后端发送请求请求该数据字典的内容。
         * @param {*} data 
         */
        handleNodeClick(data) {
            console.log("click at: ",data);
            this.$http.get(
                '/api/CMC/workrecords/system/get_data_dict_detail?dictCode=' + data.label.split("-")[0]
            ).then(response => {
                if (response.status === 200) {
                    this.currentDataDictDetail = response.data.dataDict
                    console.log("now, the current data dict detail is: ", this.currentDataDictDetail)
                    this.currentDataDictCode = data.label.split("-")[0]
                } else {
                    console.log(response.data.message)
                    this.$message.error(response.data.message)
                }
            }).catch((error) => {
                console.log(error.response.data.message)
                this.$message.error(error.response.data.message)
            })
        },

        /**
         * 打开添加数据字典的对话框
         */
        showAddDataDictDialogModal(){
            this.showAddDataDictDialog = true;  
        },

        /**
         * 打开添加数据字典条目的对话框
         */
        showAddDataDictDetailDialogModal(){
            this.showAddDataDictDetailDialog = true;  
        },

        /**
         * 关闭添加数据字典条目的对话框
         */
        closeAddDataDictDetailDialogModal(){
            this.showAddDataDictDetailDialog = false;
        },

        /**
         * 添加数据字典的表单提交事件, 向后端发送请求添加数据字典。
         */
        addDataDict(){
            this.$refs["addDataDictForm"].validate((valid) => {
                if (valid) {
                    this.$http.post(
                        '/api/CMC/workrecords/system/add_data_dict',
                        this.addDataDictForm
                    ).then(response => {
                        this.dataDictList.push(response.data.dataDict)
                        console.log("currently, data dict list is ", this.dataDictList)
                        this.$message.success("添加成功")
                        this.showAddDataDictDialog = false
                    }).catch((error) => {
                        console.log(error.response.data.message)
                        this.$message.error(error.response.data.message)
                    })   
                } else {
                    return false;
                }
            });
        },

        /**
         * 添加数据字典条目的表单提交事件, 向后端发送请求添加数据字典条目。
         */
        addDataDictDetail(){
            this.$refs["addDataDictDetailForm"].validate((valid) => {
                if (valid) {
                    var form = Object.assign({}, this.addDataDictDetailForm);
                    form["dictCode"] = this.currentDataDictCode
                    this.$http.post(
                        '/api/CMC/workrecords/system/add_data_dict_record',
                        form
                    ).then(response => {
                        this.$message.success("添加成功")
                        this.showAddDataDictDetailDialog = false
                    }).catch((error) => {
                        console.log(error.response.data.message)
                        this.$message.error(error.response.data.message)
                    })   
                } else {
                    return false;
                }
            });
        }

    },

}

</script>
  
<style scoped>
.tree-title {
    margin: 0;
    height: 40px;
    font-size: 15px;
    padding: 0 10px;
    line-height: 40px;
    border-bottom: 1px solid #d7d7d7;
    background-color: #f5f5f5
}

.el-main {
    padding: 0;
    margin-left: 20px;
    height: 100%;
    border: 1px solid #d7d7d7;
}

  .smallSizeDialog .el-dialog__body {
    padding: 0;
  }

</style>
 