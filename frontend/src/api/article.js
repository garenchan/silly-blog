import axios from '@/libs/api.request'

export const listArticle = ({since, sort, direction, page, pageSize, ...filters}) => {
  return axios.request({
    url: 'articles',
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
