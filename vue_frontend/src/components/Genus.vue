<template>
  <div class="genus">
    <b-button
      @click.prevent="select()"
      :class="[{'selected': genus.selected, 'selectable': genus.selectable}, 'pl-0 pr-1 py-1', 'taxon', genus.rank]"
      variant="link"
      :disabled="!genus.selectable"
    >
      {{ genus.name }}
    </b-button>
    <b-button
      :id="pk+'-arrow'"
      :class="[{ collapsed: genus.collapsed, 'not-collapsed': !genus.collapsed }, 'p-0']"
      v-if="(genus.num_children-genus.num_segments>0 & genus.any_child_assays)"
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
        if (!this.genus.selected) {
          this.$root.$emit('select-design', this.genus);
        } else {
          this.$root.$emit('remove-design', this.pk, this.genus.name);
        }
      }
    }
  }
}
</script>

