import env from './env'

const DEV_URL = 'http://127.0.0.1:5000/'
const PRO_URL = '/api'

export default env === 'development' ? DEV_URL : PRO_URL
