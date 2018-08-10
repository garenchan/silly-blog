import axios from '@/libs/api.request'

export const listCategories = ({since, sort, direction, page, pageSize, ...filters}) => {
  return axios.request({
    url: 'categories',
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

export const getCategory = (id) => {
  return axios.request({
    url: `categories/${id}`,
    method: 'get'
  })
}

export const createCategory = ({name, ...extras}) => {
  let data = {
    category: Object.assign({
      name: name
    }, extras)
  }
  return axios.request({
    url: 'categories',
    data,
    method: 'post'
  })
}

export const updateCategory = (id, {...info}) => {
  const data = {
    category: info
  }
  return axios.request({
    url: `categories/${id}`,
    data,
    method: 'put'
  })
}

export const deleteCategory = (id) => {
  return axios.request({
    url: `categories/${id}`,
    method: 'delete'
  })
}
