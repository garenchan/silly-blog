import axios from '@/libs/api.request'

export const login = ({ userName, password }) => {
  const data = {
    auth: {
      username: userName,
      password: password
    }
  }
  return axios.request({
    url: 'tokens',
    data,
    method: 'post'
  })
}

export const getUserInfo = () => {
  return axios.request({
    url: 'tokens',
    method: 'get'
  })
}

export const getUsersInfo = () => {
  return axios.request({
    url: 'users',
    method: 'get'
  })
}

export const logout = (token) => {

}
