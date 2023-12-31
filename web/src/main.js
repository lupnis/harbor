// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'

import VueCookies from 'vue-cookies'
import axios from 'axios'
import VueClipboard from 'vue-clipboard2'

Vue.use(VueClipboard)
Vue.config.productionTip = false
Vue.prototype.$http = axios
Vue.use(VueCookies)
/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
})
