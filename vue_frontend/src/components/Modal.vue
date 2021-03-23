<template>
  <b-modal
    :id="success? 'success-modal' : 'error-modal'"
    size="lg"
    :title="title"
    ok-only
    :ok-variant="success? 'success' : 'danger'"
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
  props: {
    success: Boolean,
    title: String,
    msg: String
  },
}
</script>
