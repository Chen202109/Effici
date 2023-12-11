// 引入基本模板
let echarts = require("echarts/lib/echarts");
// 引入提示框和title组件
require("echarts/lib/component/tooltip");
require("echarts/lib/component/title");

/**
 * @param currDocument 页面的document对象
 * @param barChartData 整个图的数据数组
 * @param barChartTitle 这张图的标题
 * @param xAxisType x轴的坐标类型，有date，value，category等等
 * @param xAxisLabelNewLine 因为有些时候，x轴的坐标分类太多，比如当有30个以上的category的时候，导致x轴的有些标签会缺失，这个输入如果为true,会将偶数的label换行形成更多空间展示
 * @param isVertical 是否是垂直柱状图
 * @param chartElementId 对应的要更新的图表元素id
 * @description 当查询之后，数据更新，根据新的数据更新柱状图的基础配置。
 * 整个图的数据是一个大数组，里面包含的每个字典是：有属性seriesName, data。这里seriesName是该series的名字，data是该series的数据。
 * data是一个数组，里面同样也是多个字典，每个字典代表着一个数据点，格式为 {‘x’: "xxx", "y": "xxx", "aaa":"aaa", "bbb":"bbb"}
 * x和y的值是用于对应图的x和y轴的值，剩下的aaa，bbb等是其他可能多的需要添加的数据标签，但是再本基础配置方法中不做处理，只做x和y的对应。
 * xAxis的type为传入的参数，有date，value，category等等，yAxis的type默认为value,因为y轴一般是数值。
 */
export function updateBarChartBasic(currDocument, barChartData, barChartTitle, xAxisType, xAxisLabelNewLine, isVertical, chartElementId) {

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
        xAxis: [],
        yAxis: [],
        series: []
    };

    let xAxisNewLineData  = addBarChartAxisData(barChartData, option, xAxisType, xAxisLabelNewLine, isVertical) 

    // 根据数据对图标添加series
    normalBarChartAddSeries(barChartData, option, isVertical)

    // 判断是否要对xAxis进行换行操作，需要在adding series之后，否则加完\n的item无法在adding series时候被filter匹配到
    isVertical ? option.xAxis[0].data = xAxisNewLineData : option.yAxis[0].data = xAxisNewLineData

    let chart = echarts.getInstanceByDom(currDocument.getElementById(chartElementId))
    chart && chart.setOption(option, true)

    console.log("updated " + chartElementId + " echart : ", chart)
}

/**
 * 当查询之后，数据更新，更新饼状图。
 * 不知道为什么，如果添加在饼状图初始化时候就设置一些参数，然后再update时候只update数据，渲染反而会变卡，所以就把所有都放到update之中来。
 * @param currDocument 页面的document对象
 * @param {Object} pieChartData 饼状图数据
 * @param {String} pieChartTitle 饼状图标题
 * @param {String} pieChartElementId 饼状图元素id
 */
export function updatePieChartBasic(currDocument, chartData, chartTitle, chartElementId){
    let chart = echarts.getInstanceByDom(currDocument.getElementById(chartElementId))

    let option = {
        title: {
            text: chartTitle,
            left: 'left'
        },
        tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b} : {c} ({d}%)'
        },
        series: [
        {
            name: chartData[0].seriesName,
            type: 'pie',
            radius: '55%',
            data: chartData[0].seriesData,
            top: '7%',
            labelLine: {
                length: 15,
                maxSurfaceAngle: 80
            },
            label: {
                alignTo: 'edge',
                formatter: '{b|{b}：}{c}次 {per|{d}%}  ',
                minMargin: 5,
                lineHeight: 15,
                // 这个配置不知道为什么，给的值越大，edge distance其实越小
                edgeDistance: 10,
                rich: {
                    b: {
                        color: '#4C5058',
                        fontWeight: 'bold',
                        lineHeight: 25
                    },
                    per: {
                        color: '#fff',
                        backgroundColor: '#4C5058',
                        padding: [3, 4],
                    }
                }
            },
            // 给标签线设置格式
            labelLayout: function (params) {
                // 通过标签魔性labelRect的x，查看是在这张图左边还是右边 （不能使用params.label.x直接看label的文字的坐标，不知道为什么直接整个回调所有设置失效）
                const isLeft = params.labelRect.x < chart.getWidth() / 2;
                const points = params.labelLinePoints;
                // 更新水平方向的标签线的末尾坐标，看是左边的标签还是右边的标签，如果是右边的标签的话就取到标签的x值也就是标签最靠左的点然后加上标签宽度
                points[2][0] = isLeft ? params.labelRect.x : params.labelRect.x + params.labelRect.width;
                // 更新竖直方向的标签线的末尾坐标，因为想要label显示在线上方，所以加上label的高度。
                points[1][1] = params.labelRect.y+params.labelRect.height
                points[2][1] = params.labelRect.y+params.labelRect.height
                return {
                    labelLinePoints: points
                };
            },
            emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
            }
        }
        ]
    };

    chart&&chart.setOption(option, true)
    console.log("updated "+chartElementId+" echart: ", chart)
}

/**
 * 将柱状图的数组信息循环添加进入柱状图的series中
 * @param {barChartData} barChartData 后端返回的包含柱状图所有信息的一个数组
 * @param {option} option 柱状图的option
 * @param {isVertical} 是否是垂直柱状图
 */
function normalBarChartAddSeries(barChartData, option, isVertical) {
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
            data: (isVertical) ? barChartData[i].seriesData.filter((item) => option.xAxis[0].data.includes(item.x)).map(item => item.y) : barChartData[i].seriesData.filter((item) => option.yAxis[0].data.includes(item.x)).map(item => item.y),
            itemStyle: {
                color: colors[i % colors.length]
            },
            label: {
                // 设置柱形图的数值
                show: true,
                position: 'top',
                align: 'center',
                // 将是0的值的label去掉
                formatter: function (params) {
                    return (params.value === 0) ? "" : params.value + "次"
                },
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

/**
 * 
 * @param {*} barChartData 柱状图的数据
 * @param {*} option 柱状图的option配置
 * @param xAxisType x轴的坐标类型，有date，value，category等等
 * @param xAxisLabelNewLine 因为有些时候，x轴的坐标分类太多，比如当有30个以上的category的时候，导致x轴的有些标签会缺失，这个输入如果为true,会将偶数的label换行形成更多空间展示
 * @param isVertical 是否是垂直柱状图
 * @returns 
 */
function addBarChartAxisData(barChartData, option, xAxisType, xAxisLabelNewLine, isVertical) {
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

    // 看看是否是竖直显示, 如果是横向显示柱状图，那么需要将x和y轴数据进行调转，然后加入option中
    let optionXAxisConfig = [{
        type: xAxisType,
        axisLabel: { interval: 0 },
        data: xAxisData
    }]
    let optionYAxisConfig = [{
        type: 'value'
    }]
    option["xAxis"] = isVertical ? optionXAxisConfig : optionYAxisConfig
    option["yAxis"] = isVertical ? optionYAxisConfig : optionXAxisConfig

    // 统计x轴所有标签的长度，用于判断是否需要x轴进行分行
    let labelTotalLength = 0
    xAxisData.forEach((item) => { labelTotalLength += countLabelLength(item) })
    if (!xAxisLabelNewLine && labelTotalLength > 55) xAxisLabelNewLine = true
    // 看看是否要给x轴数据添加换行
    let xAxisNewLineData = (xAxisLabelNewLine) ? xAxisData.map((item, index) => (index % 2 === 0) ? item : '\n' + item) : xAxisData

    return xAxisNewLineData
}

/**
 * 统计x轴所有标签的长度，避免x轴坐标标签过长，用于判断是否需要x轴进行分行，给每个substring配上权重进行计算，因为中文占得宽度长所以权重高。
 * @param {*} label 
 * @returns 这个标签经过计算之后的"长度"
 */
function countLabelLength(label) {
    let chineseSubstring = label.match(/[\u4e00-\u9fa5]/g)
    let letterSubstring = label.match(/[a-zA-Z]/g)
    let digitSubstring = label.match(/[0-9]/g)
    let punctuationSubstring = label.match(/[\s\.,\?\!]+/g)
    return (chineseSubstring ? chineseSubstring.length : 0) + (letterSubstring ? letterSubstring.length * 0.7 : 0) + (digitSubstring ? digitSubstring.length * 0.7 : 0) + (punctuationSubstring ? punctuationSubstring.length * 0.2 : 0)
}