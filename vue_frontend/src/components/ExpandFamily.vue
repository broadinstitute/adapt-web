<template>
  <div class="expandfamily">
    <b-row>
      <b-col
        v-for="taxon in taxonsExpandOrdered"
        :key="taxon[0]"
        md=6
        lg=12
        cols=12>
        <Genus v-if="taxon[1]=='genus'" :pk="taxon[0]"></Genus>
        <Species v-if="taxon[1]=='species'" :pk="taxon[0]"></Species>
      </b-col>
    </b-row>
  </div>
</template>

<script>
import Genus from '@/components/Genus.vue'
import Species from '@/components/Species.vue'
const Cookies = require('js-cookie');
// Needs CSRF for the server to accept the request
const csrfToken = Cookies.get('csrftoken')

export default {
  name: 'ExpandFamily',
  props: {
    family: String
  },
  components: {
    Genus,
    Species
  },
  data() {
    return {
      taxonsExpandOrdered: [],
    }
  },
  async created () {
    let response = await fetch('/api/taxonrank?parent=' + this.family, {
      headers: {
        "X-CSRFToken": csrfToken
      }
    })
    if (response.ok) {
      let response_json = await response.json()
      let vm = this
      for (var child in response_json) {
        if (response_json[child].any_assays | response_json[child].any_child_assays) {
          let pk = response_json[child].pk.toString()
          let selected = false
          for (let selectedDesign of vm.$root.$data.selectedDesigns) {
            if (selectedDesign[0] == pk) {
              selected = true;
              break;
            }
          }
          this.$set(vm.$root.$data.all_taxons,
            pk,
            {
              "pk": pk,
              name: response_json[child].latin_name,
              rank: response_json[child].rank,
              num_children: response_json[child].num_children,
              num_segments: response_json[child].num_segments,
              any_child_assays: response_json[child].any_child_assays,
              description: response_json[child].description,
              selectable: response_json[child].any_assays,
              taxids: response_json[child].taxons,
              shown: false,
              "selected": selected,
              collapsed: true,
            }
          )
          this.taxonsExpandOrdered.push([pk, vm.$root.$data.all_taxons[pk].rank])
        }
      }
    }
    else {
      let msg = await response.text()
      alert(msg);
    }
  }
}
</script>
