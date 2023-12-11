
/**
 * 获取 el-main containter 的主页面的组件可用的宽度
 */
export function getMainPageWidth() {
    // windows.screen.width返回屏幕宽度，减去container模型左右padding各20px, 减去侧边栏220px, 减去主页面10px的padding
    // 减去主页面的border的各1px， 减去主页面左右各15px的padding, 减去滚动条的20px，减去15px进行余量和留白
    return (window.screen.width - 20 * 2 - 220 - 10 * 2 - 1 * 2 - 15 * 2 - 20 - 15)
}