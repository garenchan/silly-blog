<template>
  <div class="error-page">
    <div class="content-con">
      <img :src="src" alt="404">
      <div class="text-con">
        <h4>{{ code }}</h4>
        <h5>{{ desc }}</h5>
      </div>
      <back-btn-group class="back-btn-group" :code="code"></back-btn-group>
    </div>
  </div>
</template>

<script>
import './error.less'
import backBtnGroup from './back-btn-group.vue'
export default {
  name: 'error_content',
  components: {
    backBtnGroup
  },
  props: {
    code: String,
    desc: String,
    src: String
  },
  methods: {
    toggleBodyClass (add) {
      if (add) {
        document.documentElement.classList.add('manage-app')
        document.body.classList.add('manage-app')
      } else {
        document.documentElement.classList.remove('manage-app')
        document.body.classList.remove('manage-app')
      }
    }
  },
  mounted () {
    this.toggleBodyClass(true)
  },
  beforeDestroy () {
    this.toggleBodyClass(false)
  }
}
</script>
