<template>
  <div>
    <div class="wrapper">
      <div class="wrapper-header">
        <nav-menu :active-key="activeKey" @on-change="handleNavMenuChange"></nav-menu>
      </div>
      <div class="wrapper-container">
        <Row>
          <i-col span="4" class="wrapper-navigate" style="background: #9ea7b4; height: 100%">
              left-side
          </i-col>
          <i-col span="16">
              <div class="wrapper-content ivu-article">
                <slot>11111</slot>
              </div>
          </i-col>
          <i-col span="4" style="background: #9ea7b4">
              right-side
          </i-col>
        </Row>
      </div>
    </div>
    <div class="footer">
      <div class="footer-main">
        <Row>
          <i-col span="5">
            <h4>
              <Icon type="logo-github"></Icon>
              GitHub
            </h4>
            <ul>
              <li>
                <a href="https://github.com/iview/iview" target="_blank">iView</a>
              </li>
              <li>
                <a href="https://github.com/iview/iview-cli" target="_blank">iView Cli</a>
              </li>
            </ul>
          </i-col>
        </Row>
      </div>
    </div>
  </div>
</template>

<script>
import navMenu from './components/menu'
export default {
  name: 'guest-main',
  components: {
    navMenu
  },
  data () {
    return {
      activeKey: ''
    }
  },
  methods: {
    handleNavMenuChange (val) {
      this.activeKey = val
    }
  }
}
</script>

<style lang="less">
@import "./main.less";
</style>
