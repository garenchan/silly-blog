<template>
  <Menu mode="horizontal" :theme="theme" :active-name="currentActiveKey" @on-select="handleSelect">
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
        <Submenu :name="menu.name" :key="menu.id" v-for="menu in navSubMenus">
          <template slot="title">
            <Icon type="ios-keypad"></Icon>
            {{ menu.name }}
          </template>
          <Menu-item :name="sub.id" :key="sub.id" v-for="sub in menu.subs">
            {{ sub.name }}
          </Menu-item>
        </Submenu>
        <Menu-item :name="item.id" :key="item.id" v-for="item in navMenuItems">
          <Icon type="ios-navigate"></Icon>
          {{ item.name }}
        </Menu-item>
      </div>
    </div>
  </Menu>
</template>

<script>
import { listCategories } from '@/api/category'

export default {
  name: 'NavMenu',
  props: {
    activeKey: String,
    theme: String
  },
  data () {
    return {
      search: '',
      currentActiveKey: this.activeKey,
      navSubMenus: [],
      navMenuItems: [],
      searchText: '搜索文章...',
      notFoundText: '未找到'
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
  },
  mounted () {
    return new Promise((resolve, reject) => {
      listCategories({ parent_id: '', sort: 'display_order', direction: 'asc' }).then(res => {
        let categories = res.categories
        for (var category of categories) {
          if (category.subs.length) this.navSubMenus.push(category)
          else this.navMenuItems.push(category)
        }
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
  width: calc(100% - 300px);
}
</style>
