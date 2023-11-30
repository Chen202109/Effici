// 引入基本模板
let echarts = require("echarts/lib/echarts");
// 引入提示框和title组件
require("echarts/lib/component/tooltip");
require("echarts/lib/component/title");

/**
 * @param barChartData 整个图的数据数组
 * @param barChartTitle 这张图的标题
 * @param xAxisType x轴的坐标类型，有date，value，category等等
 * @param xAxisLabelNewLine 因为有些时候，x轴的坐标分类太多，比如当有30个以上的category的时候，导致x轴的有些标签会缺失，这个输入如果为true,会将偶数的label换行形成更多空间展示
 * @param chartElementId 对应的要更新的图表元素id
 * @description 当查询之后，数据更新，根据新的数据更新柱状图的基础配置。
 * 整个图的数据是一个大数组，里面包含的每个字典是：有属性seriesName, data。这里seriesName是该series的名字，data是该series的数据。
 * data是一个数组，里面同样也是多个字典，每个字典代表着一个数据点，格式为 {‘x’: "xxx", "y": "xxx", "aaa":"aaa", "bbb":"bbb"}
 * x和y的值是用于对应图的x和y轴的值，剩下的aaa，bbb等是其他可能多的需要添加的数据标签，但是再本基础配置方法中不做处理，只做x和y的对应。
 * xAxis的type为传入的参数，有date，value，category等等，yAxis的type默认为value,因为y轴一般是数值。
 */
export function updateBarChartBasic(currDocument, barChartData, barChartTitle, xAxisType, xAxisLabelNewLine, chartElementId) {
    // 拿到x轴的数据
    let xAxisData = barChartData[0].seriesData.map(item => item.x)
    // 将如果所有项都是0的x轴的值去掉
    let removeList = []
    xAxisData.forEach((item) => {
        let count = 0
        barChartData.forEach(({ seriesData }) => { count = (seriesData.find(ele => ele.x === item).y === 0) ? count + 1 : count })
        if (count === barChartData.length) removeList.push(item)
    })
    xAxisData = xAxisData.filter(item => !removeList.includes(item))

    let option = {
        title: {
            top: '1%',
            left: '5%',
            text: barChartTitle,
            left: 'left'
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            }
        },
        legend: {
            top: '8%',
        },
        grid: {
            left: '3%',
            right: '3%',
            top: '23%',
            bottom: '15%',
            containLabel: true
        },
        xAxis: [
            {
                type: xAxisType,
                axisLabel: { interval: 0 },
                data: xAxisData
            }
        ],
        yAxis: [
            {
                type: 'value'
            }
        ],
        series: []
    };

    // 根据数据对图标添加series
    normalBarChartAddingSeries(barChartData, option)

    // 看看是否要给x轴数据添加换行
    xAxisData = (xAxisLabelNewLine) ? xAxisData.map((item, index) => (index % 2 === 0) ? item : '\n' + item) : xAxisData
    option.xAxis[0].data = xAxisData

    let chart = echarts.getInstanceByDom(currDocument.getElementById(chartElementId))
    chart && chart.setOption(option, true)

    console.log("updated " + chartElementId + " echart : ", chart)
}
  
/**
 * 将柱状图的数组信息循环添加进入柱状图的series中
 * @param {barChartData} barChartData 后端返回的包含柱状图所有信息的一个数组
 * @param {option} option 柱状图的option
 */
export function normalBarChartAddingSeries(barChartData, option) {
    // 指定了柱子的15种颜色，因为不设置的话echarts默认超过9个颜色会开始循环，所以扩大一点，变成15个颜色开始循环
    let colors = ["#5470C6", "#91CC75", "#FAC858", "#EE6666", "#73C0DE", "#3BA272", "#fc8452", "#a26dba", "#ea7ccc", "#ffe630", "#00A0AF", "#DB643E", "#EA8D89", "#F4B2E5", "#F03A6A"]
    for (let i = 0; i < barChartData.length; i++) {
        let series_1 = {
        name: barChartData[i].seriesName,
        type: 'bar',
        barMaxWidth: 30,
        emphasis: {
            focus: 'series'
        },
        // data: barChartData[i].seriesData.map(item=>item.y),
        data: barChartData[i].seriesData.filter((item) => option.xAxis[0].data.includes(item.x)).map(item => item.y),
        itemStyle: {
            color : colors[i%colors.length]
        },
        label: {
            // 设置柱形图的数值
            show: true,
            position: 'top',
            align: 'center',
            // formatter: function (params){
            //   return (params.value===0)?"":params.value+"次"
            // },
            formatter: '{c|{c}}次',
            rich: {
                c: {
                    // color: '#4C5058',
                    fontSize: 10,
                },
            }
        },
        }
        option.series.push(series_1)
    }
}