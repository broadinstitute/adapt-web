<template>
  <div class="design">
    <b-col cols=12 align="center" class="f-2 pb-3">Type taxa to view diagnostic assay designs for Cas13-based detection</b-col>
    <b-row class="scrolling-sticky top pb-3">
      <b-col>
        <multiselect
          v-model="selectedDesigns"
          :options="Object.values(taxons)"
          :custom-label="formatTaxa"
          :multiple="true"
          :close-on-select="false"
          :clear-on-select="false"
          :loading="loading"
          @select="select"
          @remove="remove"
          track-by="pk"
          class="top"
        ></multiselect>
      </b-col>
    </b-row>
    <div align="center" class="f-3 py-3">Or, browse through our viral assay designs below</div>
    <b-row>
      <b-col
        v-for="taxon in taxonsExpandOrdered"
        :key="taxon[0]"
        cols=12
        lg=6
        xl=4
        class="text-center text-lg-left"
      >
        <Family v-if="taxon[1]=='family'" :pk="taxon[0]"></Family>
        <Genus v-if="taxon[1]=='genus'" :pk="taxon[0]"></Genus>
        <Species v-if="taxon[1]=='species'" :pk="taxon[0]"></Species>
      </b-col>
    </b-row>
  </div>
</template>

<script>
import Family from '@/components/Family.vue'
import Genus from '@/components/Genus.vue'
import Species from '@/components/Species.vue'
import Multiselect from 'vue-multiselect'
const Cookies = require('js-cookie');
// Needs CSRF for the server to accept the request
const csrfToken = Cookies.get('csrftoken')

export default {
  name: 'Design',
  components: {
    Family,
    Genus,
    Species,
    Multiselect
  },
  data() {
    return {
      selectedDesigns: [],
      taxons: {},
      taxonsExpandOrdered: [],
      loading: true,
    }
  },
  async created () {
    let response = await fetch('/api/taxonrank?parent=null', {
      headers: {
        "X-CSRFToken": csrfToken
      }
    })
    let vm = this
    if (response.ok) {
      let response_json = await response.json()
      for (let child in response_json) {
        if (response_json[child].any_assays | response_json[child].any_child_assays) {
          let pk = response_json[child].pk.toString()
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
              selected: false,
              collapsed: true,
            }
          )
          this.taxonsExpandOrdered.push([pk, vm.$root.$data.all_taxons[pk].rank])
        }
      }
    }
    response = await fetch('/api/taxonrank?designed=true', {
      headers: {
        "X-CSRFToken": csrfToken
      }
    })
    if (response.ok) {
      let response_json = await response.json()
      for (let child in response_json) {
        let pk = response_json[child].pk.toString()
        let name = response_json[child].latin_name
        let rank = response_json[child].rank
        let taxids = response_json[child].taxons
        if (response_json[child].rank=="segment") {
          rank = response_json[child].parent_info[0]
          name = response_json[child].parent_info[1] + " — Segment " + name
          taxids = response_json[child].parent_info[2]
        }
        this.$set(vm.taxons, pk,
          {
            "pk": pk,
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
  mounted() {
    let vm = this
    vm.$root.$on('select-design', function(selectedTaxon) {
      vm.selectedDesigns.push(selectedTaxon)
      vm.select({"pk": selectedTaxon.pk, "name": selectedTaxon.name})
    });
    vm.$root.$on('remove-design', function(pk) {
      let index = -1;
      for (let i in vm.selectedDesigns) {
        if (vm.selectedDesigns[i].pk == pk) {
          index = i;
        }
      }
      if (index > -1) {
        vm.selectedDesigns.splice(index, 1);
      }
      vm.remove({"pk": pk})
    });
  },
  methods : {
    select(selectedTaxon) {
      this.$root.$data.selectedDesigns.push([selectedTaxon.pk, selectedTaxon.name])
      if (selectedTaxon.pk in this.$root.$data.all_taxons) {
        this.$root.$data.all_taxons[selectedTaxon.pk].selected = true
      }
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
      if (removedTaxon.pk in this.$root.$data.all_taxons) {
        this.$root.$data.all_taxons[removedTaxon.pk].selected = false
      }
    },
    formatTaxa({name, rank, taxids}) {
      return '[' + rank[0].toUpperCase() + rank.slice(1) + '] ' + name + " (taxid: " + taxids + ")"
    }
  }
}
</script>
