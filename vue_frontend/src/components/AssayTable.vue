<template>
  <transition appear name="fade">
    <div class="assaytable">
      <b-table small :fields="fields" :items="cluster" responsive>
        <template #table-colgroup="scope">
          <col
            v-for="field in scope.fields"
            :key="field.key"
            :style="{ width: field.key === 'show_details' ? '12%' : 'inherit' }"
          >
        </template>
        <template #cell(rank)="data">
          <a class="anchor" :id="'table-' + cluster_id + '-' + data.value.toString()"></a>
          {{ data.value + 1 }}
        </template>
        <template #cell(amplicon)="data">
          <h6>Start:</h6><p class="seq">{{ data.item.amplicon_start }}</p>
          <h6>End:</h6><p class="seq">{{ data.item.amplicon_end }}</p>
        </template>
        <template #cell(primers)="data">
          <h6>Forward:</h6>
          <p v-for="primer in data.item.left_primers.primers" :key="primer.target" class="seq">{{ primer.target }}</p>
          <h6>Reverse:</h6>
          <p v-for="primer in data.item.right_primers.primers" :key="primer.target" class="seq">{{ primer.target }}</p>
        </template>
        <template #cell(guide_set.guides)="data">
          <p v-for="guide in data.value" :key="guide.target"  class="seq">{{ guide.target }}</p>
        </template>
        <template #cell(show_details)="row">
          <b-button block size="sm" @click="row.toggleDetails" class="mr-2" pill variant="secondary">
            {{ row.detailsShowing ? 'Hide' : 'Details'}}
          </b-button>
          <b-button block size="sm" @click="vizlink(cluster_id, row.item.rank)" class="mr-2" pill variant="outline-secondary">
            Visualization
          </b-button>
        </template>
        <template #row-details="row">
          <div class="p-3 table-info">
            <b-row class="mb-2">
              <b-col>
                <label :for="'fwd-primer-' + cluster_id + row.item.rank.toString()" class='h6'>Forward Primer Statistics:</label>
                <b-table :id="'fwd-primer-' + cluster_id + row.item.rank.toString()" small :fields="fields_primer" :items="[row.item.left_primers]" responsive="sm">
                </b-table>
              </b-col>
              <b-col>
                <label :for="'rev-primer-' + cluster_id + row.item.rank.toString()" class='h6'>Reverse Primer Statistics:</label>
                <b-table :id="'fwd-primer-' + cluster_id + row.item.rank.toString()" small :fields="fields_primer" :items="[row.item.right_primers]" responsive="sm">
                </b-table>
              </b-col>
            </b-row>
            <b-row class="mb-2">
              <b-col>
                <label :for="'spacer-' + cluster_id + row.item.rank.toString()" class='h6'>Spacer Statistics:</label>
                <b-table :id="'spacer-' + cluster_id + row.item.rank.toString()" small :fields="fields_guide" :items="[row.item.guide_set]" responsive="sm">
                  <template #head(fifth_pctile_activity)="data">
                    <span v-html="data.label" class='h6'></span>
                  </template>
                  <template #table-colgroup="scope">
                    <col
                      v-for="field in scope.fields"
                      :key="field.key"
                      :style="{ width: field.key === 'fifth_pctile_activity' ? '29%' : '24%' }"
                    >
                  </template>
                </b-table>
              </b-col>
            </b-row>
          </div>
        </template>
      </b-table>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'AssayTable',
  props: {
    cluster: Array,
    cluster_id: String
  },
  data() {
    return {
      fields: [
        'rank',
        // 'objective_value',
        'amplicon',
        {key: 'primers', label: 'Primer sequences'},
        // {key: 'left_primers.primers', label: 'Left Primer'},
        // {key: 'right_primers.primers', label: 'Right Primer'},
        {key: 'guide_set.guides', label: 'Spacer sequences'},
        {key: 'show_details', label: ''},
      ],
      fields_primer: [
        {key: 'frac_bound', label: 'Fraction Bound', tdClass: 'seq'},
        {key: 'start_pos', label: 'Start Position', tdClass: 'seq'}
      ],
      fields_guide: [
        {key: 'frac_bound', label: 'Fraction Bound', tdClass: 'seq'},
        {key: 'expected_activity', label: 'Expected Activity', tdClass: 'seq'},
        {key: 'fifth_pctile_activity', label: '5<sup>th</sup> Percentile Activity', tdClass: 'seq'},
        {key: 'median_activity', label: 'Median Activity', tdClass: 'seq'}
      ],
    }
  },
  methods: {
    vizlink(cluster_id, rank) {
      this.$root.$emit('vizlink', cluster_id, rank)
    }
  }
}
</script>


