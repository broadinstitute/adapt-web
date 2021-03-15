<template>
  <transition appear name="fade">
    <div class="design">
      <DesignDetail parent="pknull"></DesignDetail>
    </div>
  </transition>
</template>

<script>
import DesignDetail from '@/components/DesignDetail.vue'

export default {
  name: 'Design',
  components: {
    DesignDetail
  }
}
</script>

<style scoped>
.collapsed .when-open,
.not-collapsed .when-closed {
  display: none !important;
}
</style>
