import Vue from 'vue'
import App from './App.vue'
import { LayoutPlugin, NavbarPlugin, CardPlugin } from 'bootstrap-vue'
import '../../assets/styles.scss'

// Make BootstrapVue Components available throughout page
Vue.use(LayoutPlugin)
Vue.use(NavbarPlugin)
Vue.use(CardPlugin)

Vue.config.productionTip = false

new Vue({
  render: h => h(App),
}).$mount('#app')
