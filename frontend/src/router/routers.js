import Main from '@/view/main'
// import store from '@/store'

export const testRouter = {
  path: '/',
  name: 'index',
  meta: {
    title: '首页',
    hideInMenu: true,
    notCache: true
  },
  component: () => {
    return import('@/view/admin/home')
  }
}

export const loginRouter = {
  path: '/login',
  name: 'login',
  meta: {
    title: 'Login - 登录',
    hideInMenu: true
  },
  component: () => import('@/view/login/login.vue')
}

export const homeRouter = {
  path: '/',
  name: '_home',
  component: Main,
  meta: {
    hideInMenu: true,
    notCache: true
  },
  children: [
    {
      path: '/home',
      name: 'home',
      meta: {
        title: '首页',
        hideInMenu: true,
        notCache: true
      },
      component: () => {
        return import('@/view/admin/home')
        // if (store.state.user.role === 'admin') return import('@/view/admin/home')
        // else if (store.state.user.role === 'user') return import('@/view/user/home')
      }
    }
  ]
}

export const adminPathPrefix = '/admin'

export const adminRouters = [
  {
    path: adminPathPrefix,
    name: 'admin',
    redirect: '/home',
    meta: {
      title: '管理员',
      hideInMenu: true,
      roles: ["admin"]
    }
  },
  {
    path: adminPathPrefix,
    name: '_admin_users',
    meta: {
      hide: true,
      roles: ["admin"]
    },
    component: Main,
    children: [
      {
        path: 'users',
        name: 'admin_users',
        meta: {
          icon: '_qq',
          title: '用户管理',
          roles: ["admin"]
        },
        component: () => import('@/view/admin/users')
      }
    ]
  },
  {
    path: adminPathPrefix,
    name: '_admin_tags',
    meta: {
      hide: true,
      roles: ["admin"]
    },
    component: Main,
    children: [
      {
        path: 'tags',
        name: 'admin_tags',
        meta: {
          icon: 'ios-pricetags',
          title: '标签管理',
          roles: ["admin"]
        },
        component: () => import('@/view/admin/tags')
      }
    ]
  },
  {
    path: adminPathPrefix,
    name: '_admin_categories',
    meta: {
      hide: true,
      roles: ["admin"]
    },
    component: Main,
    children: [
      {
        path: 'categories',
        name: 'admin_categories',
        meta: {
          icon: 'ios-switch',
          title: '分类管理',
          roles: ["admin"]
        },
        component: () => import('@/view/admin/categories')
      }
    ]
  },
  {
    path: adminPathPrefix,
    name: '_admin_subcategories',
    meta: {
      hideInMenu: true,
      roles: ["admin"]
    },
    component: Main,
    children: [
      {
        path: 'category/:category_id/subs',
        name: 'admin_subcategories',
        meta: {
          icon: 'ios-switch',
          title: '二级分类',
          roles: ["admin"]
        },
        component: () => import('@/view/admin/subcategories')
      }
    ]
  },
  {
    path: adminPathPrefix,
    name: '_admin_articles',
    meta: {
      hide: true,
      roles: ["admin"]
    },
    component: Main,
    children: [
      {
        path: 'articles',
        name: 'admin_articles',
        meta: {
          icon: 'md-bookmarks',
          title: '文章管理',
          roles: ["admin"]
        },
        component: () => import('@/view/admin/articles')
      }
    ]
  },
  {
    path: adminPathPrefix,
    name: '_admin_articles_post',
    meta: {
      hideInMenu: true,
      roles: ["admin"]
    },
    component: Main,
    children: [
      {
        path: 'article/post',
        name: 'admin_article_post',
        meta: {
          icon: 'logo-pinterest',
          title: '发表文章',
          roles: ["admin"]
        },
        component: () => import('@/view/admin/articles/post')
      }
    ]
  },
  {
    path: adminPathPrefix,
    name: '_admin_articles_edit',
    meta: {
      hideInMenu: true,
      roles: ["admin"]
    },
    component: Main,
    children: [
      {
        path: 'article/:article_id',
        name: 'admin_article_edit',
        meta: {
          icon: 'ios-create',
          title: '编辑文章',
          notCache: true,
          roles: ["admin"]
        },
        component: () => import('@/view/admin/articles/edit')
      }
    ]
  } // 其实文章编辑和发表可以使用同一个组件，但因为缓存清理问题，只能复制同一个组件2份
]

export const errorRouters = [
  {
    path: '/401',
    name: 'error_401',
    meta: {
      hideInMenu: true
    },
    component: () => import('@/view/errors/401.vue')
  },
  {
    path: '*',
    name: 'error_404',
    meta: {
      hideInMenu: true
    },
    component: () => import('@/view/errors/404.vue')
  },
]

// 所有上面定义的路由都要写在下面的routes里
export const routes = [
  testRouter,
  loginRouter,
  homeRouter,
  ...adminRouters,
  ...errorRouters
]
