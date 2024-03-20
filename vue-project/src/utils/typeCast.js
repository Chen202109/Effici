
/**
 * @description 将一个小数转成百分比格式，保留指定位数, 默认保留2位
 * @param {*} num 小数
 * @param {*} digit 小数点后的保留位数
 * @returns 百分比格式的输入
 */
export function castFloatToPercent(num, digit=2) {
    return new Intl.NumberFormat('default', {
        style: 'percent',
        minimumFractionDigits: digit,
        maximumFractionDigits: digit,
    }).format(num);
}