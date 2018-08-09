import Vue from 'vue'
import Router from 'vue-router'
import { routes } from './routers'
import store from '@/store'
import iView from 'iview'
import { getToken, canTurnTo } from '@/libs/util'

Vue.use(Router)
const router = new Router({
  routes,
  mode: 'history'
})
const LOGIN_PAGE_NAME = 'login'
const HOME_PAGE = 'home'

router.beforeEach((to, from, next) => {
  iView.LoadingBar.start()
  const token = getToken()
  const loginRequired = to.name === HOME_PAGE || to.name.startsWith('admin') || to.name.startsWith('user')
  if (!token && loginRequired) {
    next({
      name: LOGIN_PAGE_NAME, // 跳转到登录页
      query: {
        next: to.name
      }
    })
  } else if (token && loginRequired) {
    store.dispatch('getUserInfo').then(user => {
      if (canTurnTo(to.name, user.role, routes)) {
        next() // 有权限，可访问
      } else next({ replace: true, name: 'error_401' }) // 无权限，重定向到401页面
    })
  } else if (!token && to.name === LOGIN_PAGE_NAME) {
    next()
  } else if (token && to.name === LOGIN_PAGE_NAME) {
    next({
      name: 'home' // 跳转到home页
    })
  } else {
    next()
  }
})

router.afterEach(to => {
  iView.LoadingBar.finish()
  window.scrollTo(0, 0)
})

export default router
