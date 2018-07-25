import axios from '@/libs/api.request'

export const login = ({ userName, password }) => {
  const data = {
    auth: {
      method: 'password',
      password: {
        username: userName,
        password: password
      }
    }
  }
  return axios.request({
    url: '/auth/tokens',
    data,
    method: 'post'
  })
}

export const getUserInfo = (token) => {
  return axios.request({
    url: 'get_info',
    params: {
      token
    },
    method: 'get'
  })
}

export const logout = (token) => {
  return axios.request({
    url: 'logout',
    method: 'post'
  })
}
