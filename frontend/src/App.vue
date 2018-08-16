<template>
  <div id="app">
    <router-view/>
    <Back-top></Back-top>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style lang="less">
#app {
  width: 100%;
  height: 100%;
}
</style>
