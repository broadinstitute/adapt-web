import Vue from 'vue'
import App from './App.vue'
import { LayoutPlugin, NavbarPlugin, CardPlugin } from 'bootstrap-vue'
import { VuePlausible } from 'vue-plausible'
import '../../assets/styles.scss'

Vue.use(VuePlausible, {
  domain: "adapt.guide",
})

// Make BootstrapVue Components available throughout page
Vue.use(LayoutPlugin)
Vue.use(NavbarPlugin)
Vue.use(CardPlugin)

Vue.config.productionTip = false

new Vue({
  render: h => h(App),
}).$mount('#app')
