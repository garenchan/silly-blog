import axios from '@/libs/api.request'

export const listCategory = ({since, sort, direction, page, pageSize, ...filters}) => {
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
