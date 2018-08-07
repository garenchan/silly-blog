import Main from '@/view/main'

export const loginRouter = {
  path: '/login',
  name: 'login',
  meta: {
    title: 'Login - 登录',
    hideInMenu: true
  },
  component: () => import('@/view/login/login.vue')
}

// 作为Main组件的子页面展示但是不在左侧菜单显示的路由写在这里
export const otherRouter = {
  path: '/',
  name: 'otherRouter',
  redirect: '/home',
  component: Main,
  children: [
    {
      path: 'home',
      name: 'home',
      meta: {
        title: '首页',
        hideInMenu: true,
        notCache: true
      },
      component: () => import('@/view/single-page/home')
    },
    {
      path: 'admin/category/:category_id/subs',
      name: 'subcategories',
      meta: {
        icon: 'ios-switch',
        title: '二级分类',
        roles: ["admin"]
      },
      component: () => import('@/view/subcategories')
    }
  ]
}

export const appRouter = [
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
        component: () => import('@/view/users')
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
  },
  {
    path: '/admin',
    name: 'categories',
    component: Main,
    meta: {
      roles: ["admin"]
    },
    children: [
      {
        path: 'categories',
        name: '_categories',
        meta: {
          icon: 'ios-switch',
          title: '分类管理'
        },
        component: () => import('@/view/categories')
      }
    ]
  },
  {
    path: '/admin',
    name: 'articles',
    component: Main,
    meta: {
      roles: ["admin"]
    },
    children: [
      {
        path: 'articles',
        name: '_articles',
        meta: {
          icon: 'logo-pinterest',
          title: '文章管理'
        },
        component: () => import('@/view/articles')
      }
    ]
  }
]

// 所有上面定义的路由都要写在下面的routes里
export const routes = [
  loginRouter,
  otherRouter,
  ...appRouter
]
