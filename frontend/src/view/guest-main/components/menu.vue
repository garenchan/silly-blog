<template>
  <Menu mode="horizontal" :active-name="currentActiveKey" @on-select="handleSelect">
    <div class="wrapper-header-nav">
      <router-link to="/" class="wrapper-header-nav-logo">
        <img src="@/assets/images/logo-min.png">
      </router-link>
      <div class="wrapper-header-nav-search">
        <i-select ref="select"
                  v-model="search"
                  filterable
                  :placeholder="searchText"
                  :not-found-text="notFoundText"
                  @on-change="handleSearch"/>
      </div>
      <div class="wrapper-header-nav-list">
        <Menu-item name="guide">
          <Icon type="ios-navigate"></Icon>
          guide
        </Menu-item>
        <Menu-item name="component">
          <Icon type="ios-keypad"></Icon>
          component
        </Menu-item>
        <Menu-item name="live">
          <Icon type="ios-keypad"></Icon>
          live
        </Menu-item>
        <Submenu name="ecosystem">
          <template slot="title">
            <Icon type="ios-infinite"></Icon>
            ecosystem
          </template>
          <Menu-item name="cli">
            cli
          </Menu-item>
          <Menu-item name="iview-loader">
            iView Loader
          </Menu-item>
        </Submenu>
      </div>
    </div>
  </Menu>
</template>

<script>

export default {
  name: 'NavMenu',
  props: {
    activeKey: String
  },
  data () {
    return {
      search: '',
      currentActiveKey: this.activeKey,
      searchText: 'search',
      notFoundText: 'not found'
    }
  },
  watch: {
    activeKey (val) {
      this.currentActiveKey = val
    },
    currentActiveKey (val) {
      this.$emit('on-change', val)
    }
  },
  methods: {
    handleSearch (path) {
      console.log(path)
    },
    handleSelect (type) {
      console.log(type)
    }
  }
}
</script>

<style scoped>
.wrapper-header-nav .ivu-menu-item i{
  margin-right: 6px;
}
.wrapper-header .ivu-menu{
  z-index: 901;
  box-shadow: 0 1px 1px rgba(0,0,0,.08);
}
</style>
