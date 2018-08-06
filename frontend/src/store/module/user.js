import { login, logout, getUserInfo } from '@/api/user'
import { setToken, getToken } from '@/libs/util'

export default {
  state: {
    id: '',
    name: '',
    role: '',
    token: getToken(),
    avatar: ''
  },
  mutations: {
    setUserId (state, id) {
      state.id = id
    },
    setUserName (state, name) {
      state.name = name
    },
    setRole (state, role) {
      state.role = role
    },
    setToken (state, token) {
      state.token = token
      setToken(token)
    },
    setAvatar (state, avatarPath) {
      state.avatar = avatarPath
    }
  },
  actions: {
    // 登录
    handleLogin ({ commit }, {userName, password}) {
      userName = userName.trim()
      return new Promise((resolve, reject) => {
        login({
          userName,
          password
        }).then(res => {
          const token = res.token
          commit('setToken', token.id)
          resolve()
        }).catch(err => {
          reject(err)
        })
      })
    },
    // 退出登录
    handleLogOut ({ state, commit }) {
      logout(state.token)
      return new Promise((resolve, reject) => {
        commit('setToken', '')
        commit('setRole', '')
        resolve()
      })
    },
    // 获取用户相关信息
    getUserInfo ({ state, commit }) {
      return new Promise((resolve, reject) => {
        getUserInfo().then(res => {
          const user = res.token.user
          commit('setUserName', user.name)
          commit('setUserId', user.id)
          commit('setRole', user.role)
          commit('setAvatar', 'https://i.loli.net/2017/08/21/599a521472424.jpg')
          resolve(user)
        }).catch(err => {
          return reject(err)
        })
      })
    }
  }
}
