import axios from '@/libs/api.request'

export const listSources = ({...filters}) => {
  return axios.request({
    url: 'sources',
    method: 'get',
    params: filters
  })
}
