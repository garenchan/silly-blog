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

export const logout = (token) => {

}

export const getUserInfo = () => {
  return axios.request({
    url: 'tokens',
    method: 'get'
  })
}

export const listUsers = ({since, sort, direction, page, pageSize, ...filters}) => {
  return axios.request({
    url: 'users',
    method: 'get',
    params: Object.assign({
      since: since,
      sort: sort,
      direction: direction,
      page: page,
      pagesize: pageSize
    }, filters)
  })
}

export const createUser = ({name, password, roleId, ...extras}) => {
  for (var attr of ['email', 'display_name']) {
    if (!extras[attr]) delete extras[attr]
  }
  let data = {
    user: Object.assign({
      name: name,
      password: password,
      role_id: roleId,
      enabled: true
    }, extras)
  }
  return axios.request({
    url: 'users',
    data,
    method: 'post'
  })
}

export const updateUser = (id, {...info}) => {
  const data = {
    user: info
  }
  return axios.request({
    url: `users/${id}`,
    data,
    method: 'put'
  })
}

export const deleteUser = (id) => {
  return axios.request({
    url: `users/${id}`,
    method: 'delete'
  })
}
