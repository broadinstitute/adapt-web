<template>
  <transition appear name="fade">
    <div class="assaytable">
      <b-table small :fields="fields" :items="cluster" responsive>
        <template #cell(rank)="data">
          {{ data.value + 1 }}
        </template>
        <template #cell(amplicon)="data">
          <b>Start:</b> {{ data.item.amplicon_start }}
          <br>
          <b>End:</b> {{ data.item.amplicon_end }}
        </template>
        <template #cell(primers)="data">
          <b>Forward:</b>
          <p v-for="primer in data.item.left_primers.primers" :key="primer.target">{{ primer.target }}</p>
          <b>Reverse:</b>
          <p v-for="primer in data.item.right_primers.primers" :key="primer.target">{{ primer.target }}</p>
        </template>
        <template #cell(guide_set.guides)="data">
          <p v-for="guide in data.value" :key="guide.target">{{ guide.target }}</p>
        </template>
        <template #cell(show_details)="row">
          <b-button size="sm" @click="row.toggleDetails" class="mr-2 font-weight-bold" pill variant="outline-secondary">
            {{ row.detailsShowing ? 'Hide' : 'Details'}}
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
        {key: 'frac_bound', label: 'Fraction Bound'},
        {key: 'start_pos', label: 'Start Position'}
      ],
      fields_guide: [
        {key: 'frac_bound', label: 'Fraction Bound'},
        {key: 'expected_activity', label: 'Expected Activity'},
        {key: 'fifth_pctile_activity', label: 'Fifth Percentile Activity'},
        {key: 'median_activity', label: 'Median Activity'}
      ],
    }
  },
}
</script>


