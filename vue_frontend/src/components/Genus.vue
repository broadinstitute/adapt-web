<template>
  <div class="genus">
    <b-button
      @click.prevent="select()"
      :class="[{'selected': genus.selected, 'selectable': genus.selectable}, 'p-1', 'taxon', genus.rank]"
      variant="link"
      :disabled="!genus.selectable"
    >
      {{ genus.name }}
    </b-button>
    <b-button
      :id="pk+'-arrow'"
      :class="[{ collapsed: genus.collapsed, 'not-collapsed': !genus.collapsed }, 'px-1']"
      v-if="genus.num_children-genus.num_segments>0"
      v-on:click.prevent="toggle()"
      variant="link"
    >
      <b-icon-chevron-down class="arrow" :aria-label="'Toggle ' + genus.name"/>
    </b-button>
    <b-collapse :id="pk + '-toggle'" v-if="genus.shown">
      <ExpandGenus :genus="pk"></ExpandGenus>
    </b-collapse>
  </div>
</template>

<script>
import ExpandGenus from "@/components/ExpandGenus.vue"

export default {
  name: 'Genus',
  components: {
    ExpandGenus
  },
  props: {
    pk: String
  },
  data() {
    return {
      genus: {}
    }
  },
  async mounted () {
    this.genus = this.$root.$data.all_taxons[this.pk]
  },
  methods : {
    toggle() {
      this.genus.shown = true;
      this.genus.collapsed = !this.genus.collapsed;
      setTimeout(() => {
        this.$root.$emit('bv::toggle::collapse', this.pk+'-toggle');
      }, 100);
    },
    select() {
      if (this.genus.selectable) {
        /* Flip selected variable */
        this.genus.selected = !this.genus.selected;
        if (this.genus.selected) {
          /* Add to selectedDesigns */
          this.$root.$data.selectedDesigns.push([this.pk, this.genus.name])
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
    }
  }
}
</script>

