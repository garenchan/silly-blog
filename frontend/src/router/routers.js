import Main from '@/view/main'

export default [
  {
    path: '/login',
    name: 'login',
    meta: {
      title: 'Login - 登录',
      hideInMenu: true
    },
    component: () => import('@/view/login/login.vue')
  },
  {
    path: '/',
    name: '_home',
    redirect: '/home',
    component: Main,
    meta: {
      hideInMenu: true,
      notCache: true
    },
    children: [
      {
        path: 'home',
        name: 'home',
        meta: {
          hideInMenu: true,
          notCache: true
        },
        component: () => import('@/view/single-page/home')
      }
    ]
  },
  {
    path: '/admin',
    name: 'users',
    component: Main,
    meta: {
      roles: ["admin"]
    },
    children: [
      {
        path: 'users',
        name: '_users',
        meta: {
          icon: '_qq',
          title: '用户管理'
        },
        component: () => import('@/view/components/tables/user-table.vue')
      }
    ]
  },
  {
    path: '/admin',
    name: 'tags',
    component: Main,
    meta: {
      roles: ["admin"]
    },
    children: [
      {
        path: 'tags',
        name: '_tags',
        meta: {
          icon: 'ios-pricetags',
          title: '标签管理'
        },
        component: () => import('@/view/tags')
      }
    ]
  }
]