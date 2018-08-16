<template>
  <div>
    <div class="wrapper">
      <div class="wrapper-header">
        <nav-menu theme="dark" :active-key="activeKey" @on-change="handleNavMenuChange"/>
      </div>
      <div class="wrapper-container">
        <keep-alive>
          <router-view/> <!--:key="$route.path"-->
        </keep-alive>
        <BackTop/>
      </div>
    </div>
    <div class="footer">
      <div class="footer-main">
        <i-footer/>
      </div>
    </div>
  </div>
</template>

<script>
import NavMenu from './components/nav-menu'
import iFooter from './components/footer'

export default {
  name: 'guest-main',
  components: {
    NavMenu,
    iFooter
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

body{
  // overflow: auto;
}
body::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
/*正常情况下滑块的样式*/
body::-webkit-scrollbar-thumb {
  background-color: rgba(0,0,0,.05);
  border-radius: 10px;
  -webkit-box-shadow: inset 1px 1px 0 rgba(0,0,0,.1);
}
/*鼠标悬浮在该类指向的控件上时滑块的样式*/
body::-webkit-scrollbar-thumb {
  background-color: rgba(0,0,0,.2);
  border-radius: 10px;
  -webkit-box-shadow: inset 1px 1px 0 rgba(0,0,0,.1);
}
/*鼠标悬浮在滑块上时滑块的样式*/
body::-webkit-scrollbar-thumb:hover {
  background-color: rgba(0,0,0,.4);
  -webkit-box-shadow: inset 1px 1px 0 rgba(0,0,0,.1);
}
/*正常时候的主干部分*/
body::-webkit-scrollbar-track {
  border-radius: 10px;
  -webkit-box-shadow: inset 0 0 6px rgba(0,0,0,0);
  background-color: white;
}
/*鼠标悬浮在滚动条上的主干部分*/
body::-webkit-scrollbar-track:hover {
  -webkit-box-shadow: inset 0 0 6px rgba(0,0,0,.4);
  background-color: rgba(0,0,0,.01);
}
</style>
