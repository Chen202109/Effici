<template>
    <div>
        <div style="margin: 15px 0">
            <span class="demonstration" style="margin-left: 15px;">时间范围： </span>
            <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期">
            </el-date-picker>
            <el-button type="primary" @click="search">查询</el-button>
        </div>
        <!-- 容器 -->
        <div id = "saasProblemChinaMap" ref="saasProblemChinaMap" :style="{ width: getPageWidth*0.6+'px', height: '600px', margin: 'auto'}"></div>
    </div>
</template>
  
<script>
import * as echarts from 'echarts'; // 引入 ECharts 库, 该项目安装的是5.4.3版本的echarts
// 这个chinaMap.json是有完全版本的是从 https://datav.aliyun.com/portal/school/atlas/area_selector 进行获取的
// 仿照从 https://www.cnblogs.com/CandyDChen/p/13889761.html 弄下来的格式进行优化 （因为它的数据可能是筛选的数据，边境线显示太过广泛，显示不完全，台湾周围的岛也没有）
// 优化显示（南海群岛的去除，省份命名的缩减，省份label显示的居中，地图size的放大）
import chinaMap from "@/assets/json/chinaMap.json";

export default {
    name: 'AnalysisCountryData',
    data() {
        return {
            chinaMap: null,
            // 日期查询范围
            dateRange: [ new Date(new Date().getFullYear() + '-01-01'), new Date() ],
            chinaMapProvinceSaaSProblemData: [{"seriesName": "全国省份受理数据", "seriesData": 1}],
        }
    },
      // 计算页面刚加载时候渲染的属性
    computed: {
        /**
         * 获取主页面宽度的60%，用于给地图的布局的设置
         */
        getPageWidth: function(){
            // windows.screen.width返回屏幕宽度，减去侧边栏240px,减去container模型左右padding各20px和margin-right的10px,
            // 减去主页面各自15px的padding, 减去不知道那里vue自己设的30px, 减去主页面内元素和滚动条保持距离的padding-right的10px,
            return (window.screen.width-240-20*2-10-15*2-30-10)
        },
    },
    mounted() {
        // 初始化中国的地图的数据，从本地配置文件中读取
        echarts.registerMap("china", { geoJSON: chinaMap });
        // 进行图的配置
        this.drawCharts()
    },
    methods: {
        drawCharts() {
            // 在 mounted 钩子中初始化 echarts 实例，并获取容器
            this.saasProblemChinaMap = echarts.init(document.getElementById('saasProblemChinaMap'))
            // ECharts 配置项
            const  option = {
                tooltip: {
                    triggerOn: 'mousemove',
                    formatter: function (e) {
                        return e.name + '：' + e.value
                    }
                },
                // geo为地理坐标系组件，用于地图的绘制，支持在地理坐标系上绘制散点图，线集。
                geo: {
                    map: 'china', // 使用 registerMap 注册的地图名称。
                    zoom : 1.1,
                    label: {
                        show : true,
                    }
                },
                series: [
                    {
                        name: "",
                        type: 'map',
                        geoIndex: 0,
                        data: []
                    }
                ]
            }
            // 使用刚指定的配置项和数据显示图表
            this.saasProblemChinaMap.setOption(option);
        },

        async search (){
            var searchValue = {} // 存放筛选条件信息
            // 获取年、月、日，进行拼接
            for (let i = 0; i < this.dateRange.length; i++) {
                var year = this.dateRange[i].getFullYear()
                var month = ('0' + (this.dateRange[i].getMonth() + 1)).slice(-2)
                var day = ('0' + this.dateRange[i].getDate()).slice(-2)
                if (i == 0) {
                // 构建格式化后的日期字符串
                var beginData = year + '-' + month + '-' + day
                searchValue['beginData'] = beginData
                }
                if (i == 1) {
                var endData = year + '-' + month + '-' + day
                searchValue['endData'] = endData
                }
            } 
            
            this.searchSaaSCountryData(searchValue)

        },

        /**
         * 
         * @param {*} searchValue 
         */
        async searchSaaSCountryData(searchValue){
            try {
            const response = await this.$http.get(
                '/api/CMC/workrecords/analysis_saas_problem_by_country?beginData=' +
                searchValue['beginData'] +
                '&endData=' +
                searchValue['endData'] 
            )
            this.chinaMapProvinceSaaSProblemData = response.data.data
            // 把valueMax的值取出来
            let valueMax = this.chinaMapProvinceSaaSProblemData.pop()
            let saasProblemChinaMap = echarts.getInstanceByDom(document.getElementById("saasProblemChinaMap"))
            // 现在是添加属性，所以不用replace设成true，直接setOption就行
            saasProblemChinaMap&&saasProblemChinaMap.setOption({
                visualMap: {//左下角的渐变颜色条
	                min: 0,
	                max: valueMax.valueMax,
	                left: 'left',
	                top: 'bottom',
	                text: [valueMax.valueMax+"",0+""],
	                inRange: {
	                    color: ['#FCF7F6', '#FD2C05 ']
	                },
	                show:true
	            },
                series: [
                    {
                        name: this.chinaMapProvinceSaaSProblemData[0]["seriesName"],
                        type: 'map',
                        geoIndex: 0,
                        data: this.chinaMapProvinceSaaSProblemData[0]["seriesData"]
                    }
                ]
            })
            console.log('update local map data: ', this.chinaMapProvinceSaaSProblemData)

        } catch (error) {
            console.log(error)
            this.$message.error('错了哦，仔细看错误信息弹窗')
            alert('失败' + error)
      }
        }
    },
};
</script>