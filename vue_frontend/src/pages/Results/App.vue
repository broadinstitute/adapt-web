<template>
  <div id="app" class="mb-5">
  <Header page="Results"/>
  <b-container fluid id="body">
    <b-row class="mt-5">
      <b-col cols=0 md=2></b-col>
      <b-col  cols=12 md=8>
        <Results class="px-4"/>
        <AssayModal/>
        <Modal/>
      </b-col>
      <b-col cols=0 md=2></b-col>
    </b-row>
  </b-container>
  <Footer/>
  </div>
</template>

<script>
import Header from '@/components/Header.vue'
import Results from '@/components/Results.vue'
import AssayModal from '@/components/AssayModal.vue'
import Modal from '@/components/Modal.vue'
import Footer from '@/components/Footer.vue'

export default {
  name: 'App',
  components: {
    Header,
    Results,
    AssayModal,
    Modal,
    Footer
  },
}
</script>
