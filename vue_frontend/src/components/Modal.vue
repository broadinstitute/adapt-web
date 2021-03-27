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
  props: {
    variant: String,
    title: String,
    msg: String
  },
}
</script>
