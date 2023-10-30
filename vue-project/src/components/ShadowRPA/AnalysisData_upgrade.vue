<template>
  <div>
    <div class="dailyUpgradeTable">
      <el-table :data="upgradeData[0]"
        :header-cell-style="{ fontSize: '14px', background: 'rgb(64 158 255 / 65%)', color: '#696969', }"
        :row-style="{ height: '35px' }" 
        :cell-style="upgradeTableCellStyle" 
        border>
        <el-table-column v-for="(value, key) in upgradeData[0][0]" :key="key" :prop="key" :label="key"
          :width="columnWidth(key)" align="center">
        </el-table-column>
      </el-table>
    </div>
    <div class="addedUpgradeTable">
      <el-table :data="upgradeData[1]"
        :header-cell-style="{ fontSize: '14px', background: 'rgb(64 158 255 / 65%)', color: '#696969', }"
        :row-style="{ height: '35px' }" 
        :cell-style="upgradeTableCellStyle" 
        border>
        <el-table-column v-for="(value, key) in upgradeData[1][0]" :key="key" :prop="key" :label="key"
          :width="columnWidth(key)" align="center">
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>


<script>
export default {
  name: 'upgradeData',
  props: {
    upgradeData: {
        type: Array,
        default() {
          return [];
        },
      },
    },
  data() {
    return {
    }
  },
  mounted() {
    console.log(9999999);
    console.log(this.upgradeData)
  },

  methods: {
    columnWidth(key) {
      let width
      if (key.length === 4) {
        width = 75
      } else if (key.length === 5) {
        width = 85
      } else if (key.length === 6) {
        width = 110
      }
      return width
    },

    upgradeTableCellStyle(row) {
      console.log(4444)
      let style = ''
      if (row.column.label === "合计") {
        style = 'background: rgb(253 238 32 / 20%); color: red; '
      }
      style += 'font-size: 14px; '
      return style
    },
  },
}
</script>

<style>
.dailyUpgradeTable {
  float: left;
}

.addedUpgradeTable {
  float: right;
}
</style>