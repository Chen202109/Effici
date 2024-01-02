<template>
    <el-upload
        ref ="fileUpload"
        class="upload-demo"
        drag
        action=""
        :http-request="uploadFile"
        :on-change="handleChange"
        :limit="fileLimit"
        :on-exceed="handleExceed"
        :on-preview="handlePreview"
        :on-remove="handleRemove"
        :headers="headers"
        :auto-upload="false"
      >
        <i class="el-icon-upload"></i>
        <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
        <div class="el-upload__tip" slot="tip">只能上传{{this.fileLimit}}个文件，支持格式：{{ this.fileType.join('/') }}，文件不能超过{{ this.fileLimitSize}}MB</div>
    </el-upload>
</template>
  
<script>

export default {
    name: "Upload",
    props: {
        url : {
            type: String,
            default() {
                return "";
            },
        },
        fileType : {
            type: Array,
            default() {
                return [];
            }
        },
        fileLimitSize : {
            type: Number,
            default() {
                return 10;
            }
        },
        fileLimit : {
            type: Number,
            default() {
                return 1;
            }
        }
    },
    data() {
        return {
            fileList : [],
            headers: { "Content-Type": "multipart/form-data" },
        }
    },
    mounted() {

    },
    computed: {
        
    },
    methods: {
        handleChange(file, fileList){
            console.log("file: ",file)
            console.log("fileList: ",fileList)
            if (file.type != "" || file.type != null || file.type != undefined){
                //截取文件的后缀，判断文件类型
                const FileExt = file.name.replace(/.+\./, "").toLowerCase();
                //计算文件的大小
                const isSizeLt = file.size / 1024 / 1024 < this.fileLimitSize; //这里做文件大小限制
                //如果不处于限制的size范围内
                if (!isSizeLt) {
                    this.$showMessage('上传文件大小不能超过 ' + this.fileLimitSize + 'MB!');
                    // 因为就return false不会有效果，文件还是照常显示在fileList上面，upload也还是会在submit时候提交，所以直接控制他内置的fileList,将这个不符合的删除
                    fileList.splice(fileList.indexOf(file), 1);
                    return false;
                }
                //如果文件类型不在允许上传的范围内
                if(!this.fileType.includes(FileExt)){
                    this.$message.error("上传文件格式不正确!");
                    fileList.splice(fileList.indexOf(file), 1);
                    return false;
                } 
                // 类型允许，添加进自己的fileList中
                this.fileList.push(file);
                return true;
            }
        },

        /**
         * 和:http-request进行绑定的函数，覆盖el-upload本身的基础上传，el-upload组件在进行submit的时候会调用这个方法而不是那个他本身简易的方法了。用于添加一些自己本身的数据如token之类，
         * @param {*} file 
         */
        uploadFile(file){
            console.log("uploadFile", file)
            this.$http.post(
                this.url,
                file.raw
            ).then(response => {
                this.$message({
                    message: '添加成功',
                    type: 'success'
                })                
            }).catch((error) => {
                console.log(error)
                this.$message.error('错了哦，仔细看错误信息弹窗')
                alert('失败' + error)
            })
        },

        /**
         * 因为将auto-upload设置为false，所以需要手动提交，这个和外部的父组件的按钮进行绑定，父组件按钮点击，将这个组件的fileList内的文件进行上传给服务器。
         */
        submitFiles(){
            // 如果fileList为空, 因为需要他进行上传文件
            if (this.fileList.length == 0) {
                this.$message.error("文件列表为空，请上传文件!"); 
                return false;
            }

            //// 因为auto-upload设置为false，可以使用内置的submit方法进行提交，他会对每个上传的file触发:http-request绑定的函数
            // this.$refs.fileUpload.submit();

            console.log("submitFiles", this.fileList)
            var param = new FormData();
            this.fileList.forEach((val, index) => { param.append("file"+index, val.raw); });
            // 用于回调函数中指向this
            var that = this
            this.$http.post(
                this.url,
                param
            ).then(response => {
                if (response.status === 200){
                    this.$message.success("添加成功")   
                    // 将父组件的dialog给关闭, 这个需要父组件绑定这个事件
                    that.$emit("closeUploadDialog");
                }else {
                    this.$message.error(response.message);
                }       
            }).catch((error) => {
                console.log(error)
                this.$message.error('错了哦，仔细看错误信息弹窗')
            })
            
        },

        /**
         * 当超过限制文件的数量时触发
         * @param {*} files 
         * @param {*} fileList 
         */
        handleExceed(files, fileList) {
            this.$message.warning(`当前限制选择 ${this.fileLimit} 个文件，本次选择了 ${files.length} 个文件，共选择了 ${files.length + fileList.length} 个文件`);
        },

        /**
         * 当移除文件的时候触发
         * @param {*} file 
         * @param {*} fileList 
         */
        handleRemove(file, fileList) {
            this.fileList = this.fileList.filter((item) => {return item !== file});
            
        },

        /**
         * 当点击已上传（在前端，未提交给后端）的文件,将想要预览的文件进行下载
         * @param {*} file 
         */
        handlePreview(file) {
            if (window.navigator.msSaveOrOpenBlob) {
                navigator.msSaveBlob(file.raw, file.name)
            } else {
                var link = document.createElement('a')
                link.download = file.name
                link.href = window.URL.createObjectURL(file.raw)
                link.click()
                window.URL.revokeObjectURL(link.href)
            }
        },
    },

}

</script>
  
<style scoped>

</style>
 