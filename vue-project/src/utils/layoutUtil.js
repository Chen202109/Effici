
/**
 * 获取 el-main containter 的主页面的组件可用的宽度
 */
export function getMainPageWidth() {
    // windows.screen.width返回屏幕宽度，减去container模型左右padding各20px, 减去侧边栏220px, 减去主页面10px的padding
    // 减去主页面的border的各1px， 减去主页面左右各15px的padding, 减去滚动条的20px，减去15px进行余量和留白
    return (window.screen.width - 20 * 2 - 220 - 10 * 2 - 1 * 2 - 15 * 2 - 20 - 15)
}

export function columnWidth(key) {
    // 因为当标题是版本号比如V4.3.2.0的时候，表头会显示不完全，所以在生成表格column的时候将版本之中的.给给成了_,如果这时候要计算想要的宽度，就把它给改回来
    key= key.replace(/_/g, '').replace(/[^\w\u4e00-\u9fa50-9]/g, "")
    let widthDict = {
        2: 57,
        3: 70,
        4: 78,
        5: 85,
        6: 110,
        8: 135,
        10: 130,
    }
    let width = widthDict[key.length]
    return width === undefined ? 100 : width
}