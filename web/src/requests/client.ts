import axios from 'axios';
import _ from 'lodash';

const _convertKeys = (fn, o) => {
  if (o instanceof FormData) {
    let f = new FormData()
    for (let k of Array.from(o.keys())) {
      f.append(fn(k), o.get(k))
    }
    return f
  }
  
  else if (_.isArray(o)) {
    return o.map(e => _convertKeys(fn, e))
  }
  
  else if (_.isObject(o)) {
    const n = {}
    Object.keys(o).forEach(k => (n[fn(k)] = _convertKeys(fn, o[k])))
    return n
  }

  return o
};

const keysToCamel = _convertKeys.bind(null, _.camelCase)
const keysToSnake = _convertKeys.bind(null, _.snakeCase)

axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFTOKEN';

const REQUEST_URL = 'http://localhost:8000/';
const apiClient = axios.create({
  baseURL: REQUEST_URL,
  withCredentials: true, // This is the default
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
})

async function request(requestPromise: Promise<any>) {
  return await requestPromise
    .then((response) => Promise.resolve(keysToCamel(response.data)))
    .catch((error) => {
      return Promise.reject(error)
    });
}

async function get(url: string, config?: any) {
  return await request(apiClient.get(url, config));
}

async function post(url: string, payload: any, config?: any) {
  return await request(apiClient.post(url, keysToSnake(payload), config));
}

const client = {
  get,
  post,
}

export default client;