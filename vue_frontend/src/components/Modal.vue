<template>
  <b-modal
    id="msg-modal"
    size="lg"
    :header-bg-variant="variant"
    :header-text-variant="variant"
    :body-bg-variant="variant"
    :body-text-variant="variant"
    :footer-bg-variant="variant"
    :footer-text-variant="variant"
    :title="title"
    ok-only
    :ok-variant="variant"
    centered
    scrollable
  >
    <div class="b-toast-primary">
      <p v-html="msg"></p>
    </div>
  </b-modal>
</template>


<script>
export default {
  name: 'Modal',
  data() {
    return {
      // Determines what color the modal is
      // (one of 'danger', 'warning', 'info', 'success', 'dark', and 'light')
      variant: 'dark',
      // Determines the title of the modal
      title: '',
      // Determines the message within the modal
      msg: ''
    }
  },
  mounted() {
    var vm = this
    // Watch for the event 'show-msg'
    vm.$root.$on('show-msg', async function() {
      vm.title =  vm.$root.$data.modaltitle
      vm.msg =  vm.$root.$data.modalmsg
      vm.variant = vm.$root.$data.modalvariant
      // Shows the modal using BootstrapVue's watcher
      this.$bvModal.show("msg-modal")
    })
  },
}
</script>
