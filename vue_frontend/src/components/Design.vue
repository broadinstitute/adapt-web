<template>
  <div class="design">
    <multiselect
      v-model="selectedDesigns"
      :options="taxons"
      :custom-label="formatTaxa"
      :multiple="true"
      :close-on-select="false"
      :clear-on-select="false"
      :loading="loading"
      @select="select"
      @remove="remove"
      track-by="pk"
    ></multiselect>
 </div>
</template>

<script>
import Multiselect from 'vue-multiselect'
const Cookies = require('js-cookie');
// Needs CSRF for the server to accept the request
const csrfToken = Cookies.get('csrftoken')

export default {
  name: 'Design',
  components: {
    Multiselect
  },
  data() {
    return {
      selectedDesigns: [],
      taxons: [],
      loading: true,
    }
  },
  async created () {
    let response = await fetch('/api/taxonrank?designed=true', {
      headers: {
        "X-CSRFToken": csrfToken
      }
    })
    if (response.ok) {
      let response_json = await response.json()
      for (var child in response_json) {
        let name = response_json[child].latin_name
        let rank = response_json[child].rank
        let taxids = response_json[child].taxons
        if (response_json[child].rank=="segment") {
          let parent_response = await fetch('/api/taxonrank/' + response_json[child]['parent'], {
            headers: {
              "X-CSRFToken": csrfToken
            }
          })
          if (parent_response.ok) {
            let parent_response_json = await parent_response.json()
            name = parent_response_json.latin_name + " — Segment " + name
            rank = parent_response_json.rank
            taxids = parent_response_json.taxons
          }
          else {
            this.$root.$data.modaltitle = 'Error'
            this.$root.$data.modalmsg = await parent_response.text()
            this.$root.$data.modalvariant = 'danger'
            this.$root.$emit('show-msg');
          }
        }
        this.taxons.push(
          {
            "pk": response_json[child].pk.toString(),
            "name": name,
            "rank": rank,
            "description": response_json[child].description,
            "taxids": taxids,
          }
        )
      }
    }
    else {
      this.$root.$data.modaltitle = 'Error'
      this.$root.$data.modalmsg = await response.text()
      this.$root.$data.modalvariant = 'danger'
      this.$root.$emit('show-msg');
    }
    this.loading = false
  },
  methods : {
    select(selectedTaxon) {
      this.$root.$data.selectedDesigns.push([selectedTaxon.pk, selectedTaxon.name])
    },
    remove(removedTaxon){
      let index = -1;
      for (let i in this.$root.$data.selectedDesigns) {
        if (this.$root.$data.selectedDesigns[i][0] == removedTaxon.pk) {
          index = i;
        }
      }
      if (index > -1) {
        this.$root.$data.selectedDesigns.splice(index, 1);
      }
    },
    formatTaxa({name, rank, taxids}) {
      return '[' + rank[0].toUpperCase() + rank.slice(1) + '] ' + name + " (taxid: " + taxids + ")"
    }
  }
}
</script>
