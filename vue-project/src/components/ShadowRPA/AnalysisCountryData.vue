<template>
    <div>
        <!-- 容器 -->
        <div ref="saasProblemChinaMap" :style="{ width: getPageWidth, height: '600px', margin: 'auto'}"></div>
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
            return (window.screen.width-240-20*2-10-15*2-30-10)*0.6+'px'
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
            this.saasProblemChinaMap = echarts.init(this.$refs.saasProblemChinaMap);
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
                        name: 'chinaMapSeries1',
                        type: 'map',
                        geoIndex: 0,
                        data: []
                    }
                ]
            }

            // 使用刚指定的配置项和数据显示图表
            this.saasProblemChinaMap.setOption(option);
        }
    },
};
</script>