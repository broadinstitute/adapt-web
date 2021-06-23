<template>
  <b-row class="family" style="width: 100%">
    <!-- <b-col cols=11>
      <b-button
        :id="family.name+'-arrow'"
        :class="[{ collapsed: family.collapsed, 'not-collapsed': !family.collapsed }, 'px-1']"
        :disabled="family.num_children==0"
        class="pt-0 family"
        v-on:click.prevent="toggle()"
        variant="link"
      >
        {{ family.name }}
      </b-button>
    </b-col>
    <b-col cols=1 class="text-right">
      <b-form-checkbox
        :id="family.name+'check'"
        v-if="family.selectable"
        v-model="family.selected"
        :name="family.name+'-check'"
        size="lg"
        style="margin-top: 0.1rem; margin-right: -2rem;"
        inline
        @input="select()"
      ></b-form-checkbox>
    </b-col> -->
    <b-col cols=12>
      <b-button
        @click.prevent="select()"
        :class="[{'selected': family.selected, 'selectable': family.selectable}, 'p-1', 'taxon', 'family']"
        variant="link"
        :disabled="!family.selectable"
      >
        {{ family.name }}
      </b-button>
      <b-button
        :id="pk+'-arrow'"
        :class="[{'collapsed': family.collapsed, 'not-collapsed': !family.collapsed }, 'px-1']"
        v-if="family.num_children-family.num_segments>0"
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
        /* Flip selected variable */
        this.family.selected = !this.family.selected;
        if (this.family.selected) {
          /* Add to selectedDesigns */
          this.$root.$data.selectedDesigns.push([this.pk, this.family.name])
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
