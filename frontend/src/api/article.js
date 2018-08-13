import axios from '@/libs/api.request'

export const listArticles = ({since, sort, direction, page, pageSize, ...filters}) => {
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

export const getArticle = (id) => {
  return axios.request({
    url: `articles/${id}`,
    method: 'get'
  })
}

export const createArticle = ({title, content, sourceId, categoryId, ...extras}) => {
  let data = {
    article: Object.assign({
      title: title,
      content: content,
      source_id: sourceId,
      category_id: categoryId
    }, extras)
  }
  return axios.request({
    url: 'articles',
    data,
    method: 'post'
  })
}

export const updateArticle = (id, {...info}) => {
  const data = {
    article: info
  }
  return axios.request({
    url: `articles/${id}`,
    data,
    method: 'put'
  })
}

export const deleteArticle = (id) => {
  return axios.request({
    url: `articles/${id}`,
    method: 'delete'
  })
}
