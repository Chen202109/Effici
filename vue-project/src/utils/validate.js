/* 去除空格的工具函数 目前用于登录login控件 vue-project\src\views\login.vue */
export function validUsername(str) {
  const valid_map = ['admin', 'editor']
  return valid_map.indexOf(str.trim()) >= 0
}