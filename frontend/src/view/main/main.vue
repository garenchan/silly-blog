<template>
  <Layout style="height: 100%" class="main">
    <Sider hide-trigger collapsible :width="256" :collapsed-width="64" v-model="collapsed" class="left-sider" :style="{overflow: 'hidden'}">
      <side-menu accordion ref="sideMenu" :active-name="$route.name" :collapsed="collapsed" @on-select="turnToPage" :menu-list="menuList">
        <!-- 需要放在菜单上面的内容，如Logo，写在side-menu标签内部，如下 -->
        <div class="logo-con">
          <img v-show="!collapsed" :src="maxLogo" key="max-logo" />
          <img v-show="collapsed" :src="minLogo" key="min-logo" />
        </div>
      </side-menu>
    </Sider>
    <Layout>
      <Header class="header-con">
        <header-bar :collapsed="collapsed" @on-coll-change="handleCollapsedChange">
          <user :user-avator="userAvator"/>
          <language @on-lang-change="setLocal" style="margin-right: 10px;" :lang="local"/>
          <fullscreen v-model="isFullscreen" style="margin-right: 10px;"/>
        </header-bar>
      </Header>
      <Content class="main-content-con">
        <Layout class="main-layout-con">
          <div class="tag-nav-wrapper">
            <tags-nav :value="$route" @input="handleClick" :list="tagNavList" @on-close="handleCloseTag"/>
          </div>
          <Content id="content" class="content-wrapper nui-scroll">
            <keep-alive :include="cacheList">
              <router-view/> <!--:key="$route.path"-->
            </keep-alive>
            <BackTop parentId="content" :height="300"/>
            <!--<keep-alive>
              <router-view v-if="!($route.meta && $route.meta.notCache)"></router-view>
            </keep-alive>
            <router-view v-if="$route.meta && $route.meta.notCache"></router-view>-->
          </Content>
        </Layout>
      </Content>
    </Layout>
  </Layout>
</template>
<script>
import BackTop from '_c/back-top'
import SideMenu from './components/side-menu'
import HeaderBar from './components/header-bar'
import TagsNav from './components/tags-nav'
import User from './components/user'
import Fullscreen from './components/fullscreen'
import Language from './components/language'
import { mapMutations, mapActions } from 'vuex'
import { getNewTagList, getNextName } from '@/libs/util'
import minLogo from '@/assets/images/logo-min.png'
import maxLogo from '@/assets/images/logo.png'
import './main.less'
export default {
  name: 'Main',
  components: {
    BackTop,
    SideMenu,
    HeaderBar,
    Language,
    TagsNav,
    Fullscreen,
    User
  },
  data () {
    return {
      collapsed: false,
      minLogo,
      maxLogo,
      isFullscreen: false
    }
  },
  computed: {
    tagNavList () {
      return this.$store.state.app.tagNavList
    },
    tagRouter () {
      return this.$store.state.app.tagRouter
    },
    userAvator () {
      return this.$store.state.user.avatar
    },
    cacheList () {
      return this.tagNavList.length ? this.tagNavList.filter(item => !(item.meta && item.meta.notCache)).map(item => item.name) : []
    },
    menuList () {
      return this.$store.getters.menuList
    },
    local () {
      return this.$store.state.app.local
    }
  },
  methods: {
    ...mapMutations([
      'setBreadCrumb',
      'setTagNavList',
      'addTag',
      'setLocal'
    ]),
    ...mapActions([
      'handleLogin'
    ]),
    turnToPage (name) {
      if (name.indexOf('isTurnByHref_') > -1) {
        window.open(name.split('_')[1])
        return
      }
      this.$router.push({
        name: name
      })
    },
    handleCollapsedChange (state) {
      this.collapsed = state
    },
    handleCloseTag (res, type, name) {
      const nextName = getNextName(this.tagNavList, name)
      this.setTagNavList(res)
      let openName = ''
      if (type === 'all') {
        this.turnToPage('home')
        openName = 'home'
      } else if (this.$route.name === name) {
        this.$router.push({ name: nextName })
        openName = nextName
      }
      this.$refs.sideMenu.updateOpenName(openName)
    },
    handleClick (item) {
      let name = item.name
      let routerObj = { name }
      if (item.params) routerObj.params = item.params
      if (item.query) routerObj.query = item.query
      this.$router.push(routerObj)
    },
    /* 管理后台的body样式和游客前台的不一样, 需要进行切换 */
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
  watch: {
    '$route' (newRoute) {
      this.setBreadCrumb(newRoute.matched)
      this.setTagNavList(getNewTagList(this.tagNavList, newRoute))
    }
  },
  mounted () {
    /**
     * @description 初始化设置面包屑导航和标签导航
     */
    this.toggleBodyClass(true)
    this.setTagNavList()
    this.addTag(this.$store.state.app.homeRoute)
    this.setBreadCrumb(this.$route.matched)
    // 设置初始语言
    this.setLocal(this.$i18n.locale)
  },
  destroyed () {
    this.toggleBodyClass(false)
  }
}
</script>

<style lang="less">
.nui-scroll{
  // overflow: auto;
}
.nui-scroll::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
/*正常情况下滑块的样式*/
.nui-scroll::-webkit-scrollbar-thumb {
  background-color: rgba(0,0,0,.05);
  border-radius: 10px;
  -webkit-box-shadow: inset 1px 1px 0 rgba(0,0,0,.1);
}
/*鼠标悬浮在该类指向的控件上时滑块的样式*/
.nui-scroll:hover::-webkit-scrollbar-thumb {
  background-color: rgba(0,0,0,.2);
  border-radius: 10px;
  -webkit-box-shadow: inset 1px 1px 0 rgba(0,0,0,.1);
}
/*鼠标悬浮在滑块上时滑块的样式*/
.nui-scroll::-webkit-scrollbar-thumb:hover {
  background-color: rgba(0,0,0,.4);
  -webkit-box-shadow: inset 1px 1px 0 rgba(0,0,0,.1);
}
/*正常时候的主干部分*/
.nui-scroll::-webkit-scrollbar-track {
  border-radius: 10px;
  -webkit-box-shadow: inset 0 0 6px rgba(0,0,0,0);
  background-color: white;
}
/*鼠标悬浮在滚动条上的主干部分*/
.nui-scroll::-webkit-scrollbar-track:hover {
  -webkit-box-shadow: inset 0 0 6px rgba(0,0,0,.4);
  background-color: rgba(0,0,0,.01);
}
</style>
