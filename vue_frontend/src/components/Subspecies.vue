<template>
  <div class="subspecies">
    <b-button
      @click.prevent="select()"
      :class="[{'selected': subspecies.selected, 'selectable': subspecies.selectable}, 'p-0', 'taxon', subspecies.rank]"
      variant="link"
      :disabled="!subspecies.selectable"
    >
      {{ subspecies.name }}
    </b-button>
    <span v-if="subspecies.num_segments>0">
      -
      <span
        v-for="(segment, i) in segmentsOrdered"
        :key="segment"
      >
        <b-button
        @click.prevent="select_seg(segment)"
        :class="[{'selected': root.$data.all_taxons[segment].selected, 'selectable': root.$data.all_taxons[segment].selectable}, 'p-1', 'taxon', root.$data.all_taxons[segment].rank]"
        variant="link"
        :disabled="!root.$data.all_taxons[segment].selectable"
        >
          {{ root.$data.all_taxons[segment].shortname }}
        </b-button>
      <span v-if="i<subspecies.num_segments-1">|</span>
      </span>
    </span>
  </div>
</template>

<script>
const Cookies = require('js-cookie');
// Needs CSRF for the server to accept the request
const csrfToken = Cookies.get('csrftoken')

export default {
  name: 'Subspecies',
  props: {
    pk: String
  },
  data() {
    return {
      subspecies: {},
      segmentsOrdered: [],
      root: this.$root
    }
  },
  async mounted () {
    this.subspecies = this.$root.$data.all_taxons[this.pk]
    if (this.subspecies.num_segments > 0) {
      let response = await fetch('/api/taxonrank?rank=segment&parent=' + this.pk, {
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
                name: vm.subspecies.name + " — Segment " + response_json[child].latin_name,
                shortname: response_json[child].latin_name,
                rank: vm.subspecies.rank,
                num_children: response_json[child].num_children,
                num_segments: response_json[child].num_segments,
                any_child_assays: response_json[child].any_child_assays,
                description: response_json[child].description,
                selectable: response_json[child].any_assays,
                taxids: vm.subspecies.taxids,
                shown: false,
                "selected": selected,
                collapsed: true,
              }
            )
          this.segmentsOrdered.push(pk)
          }
        }
      }
    }
  },
  methods : {
    toggle() {
      this.subspecies.shown = true;
      this.subspecies.collapsed = !this.subspecies.collapsed;
      setTimeout(() => {
        this.$root.$emit('bv::toggle::collapse', this.pk+'-toggle');
      }, 100);
    },
    select() {
      if (this.subspecies.selectable) {
        if (!this.subspecies.selected) {
          this.$root.$emit('select-design', this.subspecies);
        } else {
          this.$root.$emit('remove-design', this.pk, this.subspecies.name);
        }
      }
    },
    select_seg(segment) {
      if (this.$root.$data.all_taxons[segment].selectable) {
        if (!this.$root.$data.all_taxons[segment].selected) {
          this.$root.$emit('select-design', this.$root.$data.all_taxons[segment]);
        } else {
          this.$root.$emit('remove-design', segment);
        }
      }
    }
  }
}
</script>

