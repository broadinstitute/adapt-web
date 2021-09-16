import Vue from 'vue'
import App from './App.vue'
import { LayoutPlugin, NavbarPlugin, ModalPlugin, TabsPlugin, TablePlugin, ButtonPlugin, BIconChevronDown, OverlayPlugin, BIconPlus, BIconDash, BIconInfoCircle, BIconDownload, VBTooltip } from 'bootstrap-vue'
import '../../assets/styles.scss'

// Make BootstrapVue Components available throughout page
Vue.use(LayoutPlugin)
Vue.use(NavbarPlugin)
Vue.use(ModalPlugin)
Vue.use(TabsPlugin)
Vue.use(TablePlugin)
Vue.use(ButtonPlugin)
Vue.use(OverlayPlugin)
Vue.directive('b-tooltip', VBTooltip)
Vue.component('b-icon-chevron-down', BIconChevronDown)
Vue.component('b-icon-plus', BIconPlus)
Vue.component('b-icon-dash', BIconDash)
Vue.component('b-icon-info-circle', BIconInfoCircle)
Vue.component('b-icon-download', BIconDownload)

Vue.config.productionTip = false

new Vue({
  render: h => h(App),
}).$mount('#app')
