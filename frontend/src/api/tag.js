import axios from '@/libs/api.request'

export const getTags = ({since, sort, direction, page, pageSize}) => {
  return axios.request({
    url: 'tags',
    method: 'get',
    params: {
      since: since,
      sort: sort,
      direction: direction,
      page: page,
      pagesize: pageSize
    }
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
