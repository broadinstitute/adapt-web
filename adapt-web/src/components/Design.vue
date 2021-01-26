<template>
  <div class="design">
    <h1>{{ family }}</h1>
    <h2>{{ genus }}</h2>
    <h3>{{ species }}</h3>
    <h4>{{ subspecies }}</h4>
  </div>
</template>

<script>
export default {
  name: 'Design',
  props: {
    family: String,
    genus: String,
    species: String,
    subspecies: String,
  }
}
</script>
