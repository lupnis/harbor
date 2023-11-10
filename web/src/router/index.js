import Vue from 'vue'
import Router from 'vue-router'
import HarborMainPage from '@/components/HarborMainPage'
import HarborErrorPage from '@/components/HarborErrorPage'
import HarborFetchPage from '@/components/HarborFetchPage'
import HarborUploadPage from '@/components/HarborUploadPage'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'HarborMainPage',
      component: HarborMainPage
    },
    {
      path: '/error',
      name: 'HarborErrorPage',
      component: HarborErrorPage
    },
    {
      path: '/fetch',
      name: 'HarborFetchPage',
      component: HarborFetchPage
    },
    {
      path: '/create',
      name: 'HarborUploadPage',
      component: HarborUploadPage
    }
  ]
})
