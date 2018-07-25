import env from './env'

const DEV_URL = '127.0.0.1:8888'
const PRO_URL = '/api'

export default env === 'development' ? DEV_URL : PRO_URL
