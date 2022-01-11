import Vue from 'vue'
import App from './App.vue'
import { LayoutPlugin, NavbarPlugin, ButtonGroupPlugin } from 'bootstrap-vue'
import { VuePlausible } from 'vue-plausible'
import '../../assets/styles.scss'

Vue.use(VuePlausible, {
  domain: "adapt.guide",
  enableAutoPageviews: true,
})


// Make BootstrapVue Components available throughout page
Vue.use(LayoutPlugin)
Vue.use(NavbarPlugin)
Vue.use(ButtonGroupPlugin)

Vue.config.productionTip = false

new Vue({
  render: h => h(App),
}).$mount('#app')
