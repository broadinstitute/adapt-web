<template>
  <div class="species">
    <b-button
      @click.prevent="select()"
      :class="[{'selected': species.selected, 'selectable': species.selectable}, 'p-1', 'taxon', species.rank]"
      variant="link"
      :disabled="!species.selectable"
    >
      {{ species.name }}
    </b-button>
    <span v-if="species.num_segments>0">
      <span
        v-for="segment in Object.keys(segments)"
        :key="segment"
      >
        <b-button
        @click.prevent="select_seg(segment)"
        :class="[{'selected': segments[segment].selected, 'selectable': segments[segment].selectable}, 'p-1', 'taxon', segments[segment].rank]"
        variant="link"
        :disabled="!segments[segment].selectable"
      >
        {{ segments[segment].name }}
      </b-button>
      </span>
    </span>
    <b-button
      :id="pk+'-arrow'"
      :class="[{ collapsed: species.collapsed, 'not-collapsed': !species.collapsed }, 'px-1']"
      v-if="species.num_children-species.num_segments>0"
      v-on:click.prevent="toggle()"
      variant="link"
    >
      <b-icon-chevron-down font-scale="1" :aria-label="'Toggle ' + species.name"/>
    </b-button>
    <b-collapse :id="pk + '-toggle'" v-if="species.shown">
      <ExpandSpecies :species="pk"></ExpandSpecies>
    </b-collapse>
  </div>
</template>

<script>
import ExpandSpecies from "@/components/ExpandSpecies.vue"
const Cookies = require('js-cookie');
// Needs CSRF for the server to accept the request
const csrfToken = Cookies.get('csrftoken')

export default {
  name: 'Species',
  components: {
    ExpandSpecies
  },
  props: {
    pk: String
  },
  data() {
    return {
      species: {},
      segments: {}
    }
  },
  async mounted () {
    this.species = this.$root.$data.all_taxons[this.pk]
    if (this.species.num_segments > 0) {
      let response = await fetch('/api/taxonrank?rank=segment&parent=' + this.pk.slice(2), {
        headers: {
          "X-CSRFToken": csrfToken
        }
      })
      if (response.ok) {
        let response_json = await response.json()
        let vm = this
        for (var child in response_json) {
          this.$set(vm.$root.$data.all_taxons,
            "pk" + response_json[child].pk.toString(),
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
          this.$set(this.segments,
            "pk" + response_json[child].pk.toString(),
            {
              name: response_json[child].latin_name,
              description: response_json[child].description,
              selectable: response_json[child].any_assays,
              shown: false,
              selected: false,
              collapsed: true,
            }
          )
        }
      }
    }
  },
  methods : {
    toggle() {
      this.species.shown = true;
      this.species.collapsed = !this.species.collapsed;
      setTimeout(() => {
        this.$root.$emit('bv::toggle::collapse', this.pk+'-toggle');
      }, 100);
    },
    select() {
      if (this.species.selectable) {
        /* Flip selected variable */
        this.species.selected = !this.species.selected;
        if (this.species.selected) {
          /* Add to selectedDesigns */
          this.$root.$data.selectedDesigns.push([this.pk, this.species.name])
        } else {
          /* Remove from selectedDesigns */
          let index = -1;
          for (let i in this.$root.$data.selectedDesigns) {
            if (this.$root.$data.selectedDesigns[i][0] == this.pk) {
              index = i;
            }
          }
          if (index > -1) {
            this.$root.$data.selectedDesigns.splice(index, 1);
          }
        }
        /* Resort selectedDesigns by primary key order */
        this.$root.$data.selectedDesigns.sort();
      }
    },
    select_seg(segment) {
      if (this.segments[segment].selectable) {
        /* Flip selected variable */
        this.segments[segment].selected = !this.segments[segment].selected;
        if (this.segments[segment].selected) {
          /* Add to selectedDesigns */
          this.$root.$data.selectedDesigns.push([segment, this.segments[segment].name])
        } else {
          /* Remove from selectedDesigns */
          let index = -1;
          for (let i in this.$root.$data.selectedDesigns) {
            if (this.$root.$data.selectedDesigns[i][0] == segment) {
              index = i;
            }
          }
          if (index > -1) {
            this.$root.$data.selectedDesigns.splice(index, 1);
          }
        }
        /* Resort selectedDesigns by primary key order */
        this.$root.$data.selectedDesigns.sort();
      }
    }
  }
}
</script>

