<template>
  <div class="analysisUpgrade-version">
    <version :versionData="analysisUpgrade"></version>
  </div>

</template>

<script>
import version from '@/components/ShadowRPA/AnalysisUpgrade_version.vue'

export
default {
  name: 'analysisUpgrade-version',
  components: {
    version
  },
  data() {
    return {
        analysisUpgrade:[1,2]
    }
  },
  methods: {
  }
}

</script>

<style>
</style>