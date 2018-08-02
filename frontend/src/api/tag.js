import axios from '@/libs/api.request'

export const listTags = ({since, sort, direction, page, pageSize, ...filters}) => {
  return axios.request({
    url: 'tags',
    method: 'get',
    params: Object.assign({}, {
      since: since,
      sort: sort,
      direction: direction,
      page: page,
      pagesize: pageSize
    }, filters)
  })
}

export const createTag = (name) => {
  const data = {
    tag: {
      name: name.trim()
    }
  }
  return axios.request({
    url: 'tags',
    data,
    method: 'post'
  })
}

export const updateTag = (id, {...info}) => {
  const data = {
    tag: info
  }
  return axios.request({
    url: `tags/${id}`,
    data,
    method: 'put'
  })
}

export const deleteTag = (id) => {
  return axios.request({
    url: `tags/${id}`,
    method: 'delete'
  })
}
