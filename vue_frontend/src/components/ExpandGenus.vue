<template>
  <div class="expandgenus">
    <span
      v-for="taxon in Object.keys(taxons)"
      :key="taxon"
    >
      <Species v-if="taxons[taxon].rank=='species'" :pk="taxon"></Species>
    </span>
  </div>
</template>

<script>
import Species from '@/components/Species.vue'
const Cookies = require('js-cookie');
// Needs CSRF for the server to accept the request
const csrfToken = Cookies.get('csrftoken')

export default {
  name: 'ExpandGenus',
  props: {
    genus: String
  },
  components: {
    Species
  },
  data() {
    return {
      taxons: {},
    }
  },
  async created () {
    let response = await fetch('/api/taxonrank?parent=' + this.genus, {
      headers: {
        "X-CSRFToken": csrfToken
      }
    })
    if (response.ok) {
      let response_json = await response.json()
      let vm = this
      for (var child in response_json) {
        this.$set(vm.$root.$data.all_taxons,
          response_json[child].pk.toString(),
          {
            name: response_json[child].latin_name,
            rank: response_json[child].rank,
            num_children: response_json[child].num_children,
            num_segments: response_json[child].num_segments,
            description: response_json[child].description,
            selectable: response_json[child].any_assays,
            shown: false,
            selected: false,
            collapsed: true,
          }
        )
        this.$set(this.taxons,
          response_json[child].pk.toString(),
          {
            name: response_json[child].latin_name,
            rank: response_json[child].rank,
            num_children: response_json[child].num_children,
            num_segments: response_json[child].num_segments,
            description: response_json[child].description,
            selectable: response_json[child].any_assays,
            shown: false,
            selected: false,
            collapsed: true,
          }
        )
      }
    }
    else {
      let msg = await response.text()
      alert(msg);
    }
  }
}
</script>
