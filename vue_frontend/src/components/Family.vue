<template>
  <b-row class="family" style="width: 100%">
    <b-col cols=12>
      <b-button
        @click.prevent="select()"
        :class="[{'selected': family.selected, 'selectable': family.selectable}, 'px-0 py-1', 'taxon', 'family']"
        variant="link"
        :disabled="!family.selectable"
      >
        {{ family.name }}
      </b-button>
      <b-button
        :id="pk+'-arrow'"
        :class="[{'collapsed': family.collapsed, 'not-collapsed': !family.collapsed }, 'p-0']"
        v-if="(family.num_children-family.num_segments>0 & family.any_child_assays)"
        v-on:click.prevent="toggle()"
        variant="link"
      >
        <b-icon-chevron-down class="arrow" :aria-label="'Toggle ' + family.name"/>
      </b-button>
    </b-col>
    <b-col cols=12>
      <b-collapse :id="pk + '-toggle'" v-if="family.shown">
        <ExpandFamily :family="pk"></ExpandFamily>
      </b-collapse>
    </b-col>
    </b-row>
</template>

<script>
import ExpandFamily from '@/components/ExpandFamily.vue'

export default {
  name: 'Family',
  components: {
    ExpandFamily
  },
  props: {
    pk: String
  },
  data() {
    return {
      family: {}
    }
  },
  async mounted () {
    this.family = this.$root.$data.all_taxons[this.pk]
  },
  methods : {
    toggle() {
      this.family.shown = true;
      this.family.collapsed = !this.family.collapsed;
      setTimeout(() => {
        this.$root.$emit('bv::toggle::collapse', this.pk+'-toggle');
      }, 100);
    },
    select() {
      if (this.family.selectable) {
        if (!this.family.selected) {
          this.$root.$emit('select-design', this.family);
        } else {
          this.$root.$emit('remove-design', this.pk, this.family.name);
        }
      }
    }
  }
}
</script>
