import axios from '@/libs/api.request'

export const listRoles = ({...filters}) => {
  return axios.request({
    url: 'roles',
    method: 'get',
    params: filters
  })
}
