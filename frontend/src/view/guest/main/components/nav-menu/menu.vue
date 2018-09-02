<template>
  <Menu ref="menu"
        mode="horizontal"
        :theme="theme"
        :active-name="currentActiveKey"
        @on-select="handleSelect">
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
        <template v-for="menu in navMenus">
          <Submenu v-if="menu.subs.length" :name="menu.name" :key="menu.id">
            <template slot="title">
              <Icon type="ios-keypad"></Icon>
              {{ menu.name }}
            </template>
            <Menu-item :name="sub.name" :key="sub.id" :to="{ name: 'guest_category', params: { category_id: sub.id }}" v-for="sub in menu.subs">
              {{ sub.name }}
            </Menu-item>
          </Submenu>
          <Menu-item v-else :name="menu.name" :key="menu.id" :to="{ name: 'guest_category', params: { category_id: menu.id }}">
            <Icon type="ios-navigate"></Icon>
            {{ menu.name }}
          </Menu-item>
        </template>
      </div>
    </div>
  </Menu>
</template>

<script>
import { listCategories } from '@/api/category'

export default {
  name: 'NavMenu',
  props: {
    theme: String
  },
  data () {
    return {
      search: '',
      navMenus: [],
      searchText: '搜索文章...',
      notFoundText: '未找到'
    }
  },
  computed: {
    currentActiveKey () {
      return this.$store.state.guestNavMenu.activeKey
    }
  },
  methods: {
    handleSearch (path) {
      console.log(path)
    },
    handleSelect (type) {
      console.log(type)
    }
  },
  mounted () {
    return new Promise((resolve, reject) => {
      listCategories({ parent_id: '', sort: 'display_order', direction: 'asc' }).then(res => {
        this.navMenus = res.categories
      }).catch(err => {
        console.log('load categories failed:' + err)
      })
    })
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
.wrapper-header-nav-list {
  /* width: calc(100% - 300px); */
}
</style>
