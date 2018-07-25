import { login, getUserInfo } from '@/api/user'

export default {
  state: {
  },
  mutations: {

  },
  actions: {
    // 登录
    handleLogin ({ commit }, {userName, password}) {
      userName = userName.trim()
      console.log(userName + ':' + password)
      return new Promise((resolve, reject) => {
        login({
          userName,
          password
        }).then(res => {
          const data = res.data
          console.log(data)
          // commit('setToken', data.token)
          resolve()
        }).catch(err => {
          reject(err)
        })
      })
    },
    // 获取用户相关信息
    getUserInfo ({ state, commit }) {
      console.log('get user info')
    }
  }
}
