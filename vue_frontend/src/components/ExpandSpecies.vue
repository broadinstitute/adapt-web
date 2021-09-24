<template>
  <div class="expandspecies">
    <div
      v-for="taxon in taxonsExpandOrdered"
      :key="taxon"
    >
      <Subspecies :pk="taxon"></Subspecies>
    </div>
  </div>
</template>

<script>
import Subspecies from '@/components/Subspecies.vue'
const Cookies = require('js-cookie');
// Needs CSRF for the server to accept the request
const csrfToken = Cookies.get('csrftoken')

export default {
  name: 'ExpandSpecies',
  props: {
    species: String
  },
  components: {
    Subspecies
  },
  data() {
    return {
      taxons: {},
      taxonsExpandOrdered: [],
    }
  },
  async created () {
    let response = await fetch('/api/taxonrank?rank=subspecies&parent=' + this.species, {
      headers: {
        "X-CSRFToken": csrfToken
      }
    })
    if (response.ok) {
      let response_json = await response.json()
      let vm = this
      for (var child in response_json) {
        let pk = response_json[child].pk.toString()
        this.$set(vm.$root.$data.all_taxons,
          pk,
          {
            "pk": pk,
            name: response_json[child].latin_name,
            rank: response_json[child].rank,
            num_children: response_json[child].num_children,
            num_segments: response_json[child].num_segments,
            description: response_json[child].description,
            selectable: response_json[child].any_assays,
            taxids: response_json[child].taxons,
            shown: false,
            selected: false,
            collapsed: true,
          }
        )
        this.$set(this.taxons,
          pk,
          {
            "pk": pk,
            name: response_json[child].latin_name,
            rank: response_json[child].rank,
            num_children: response_json[child].num_children,
            num_segments: response_json[child].num_segments,
            description: response_json[child].description,
            selectable: response_json[child].any_assays,
            taxids: response_json[child].taxons,
            shown: false,
            selected: false,
            collapsed: true,
          }
        )
        this.taxonsExpandOrdered.push(pk)
      }
    }
    else {
      let msg = await response.text()
      alert(msg);
    }
  }
}
</script>
