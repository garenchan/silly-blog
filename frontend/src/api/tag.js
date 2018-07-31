import axios from '@/libs/api.request'

export const getTagsInfo = () => {
  return axios.request({
    url: 'tags',
    method: 'get'
  })
}
