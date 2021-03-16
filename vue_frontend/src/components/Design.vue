<template>
  <div class="design">
   <div
      v-for="taxon in Object.keys(taxons)"
      :key="taxon"
    >
      <h1 :class="taxons[taxon].rank">
        <a @click="select(taxon)" :class="[{'selected': taxons[taxon].selected, 'selectable': taxons[taxon].selectable}, 'p-1', 'taxon']" :href="'#' + taxon + '-toggle'">{{ taxons[taxon].name }}</a>
        <a
          :id="taxon+'-arrow'"
          :class="{ collapsed: taxons[taxon].collapsed, 'not-collapsed': !taxons[taxon].collapsed }"
          :href="'#' + taxon + '-toggle'"
          v-if="taxons[taxon].num_children>0"
          v-on:click="toggle(taxon)"
          @click.prevent
        >
          <b-icon-chevron-down class="arrow mx-2" :aria-label="'Toggle ' + taxons[taxon].name"/>
        </a>
      </h1>
      <b-collapse :id="taxon + '-toggle'" v-if="taxons[taxon].shown">
        <Design :parent="taxon"></Design>
      </b-collapse>
    </div>
  </div>
</template>

<script>
const Cookies = require('js-cookie');
// Needs CSRF for the server to accept the request
const csrfToken = Cookies.get('csrftoken')

export default {
  name: 'Design',
  props: {
    parent: String
  },
  data() {
    return {
      taxons: {},
    }
  },
  async created () {
    let response = await fetch('/api/taxonrank?parent=' + this.parent.slice(2), {
      headers: {
        "X-CSRFToken": csrfToken
      }
    })
    if (response.ok) {
      let response_json = await response.json()
      for (var child in response_json) {
        this.$set(this.taxons,
          "pk" + response_json[child].pk.toString(),
          {
            name: response_json[child].latin_name,
            rank: response_json[child].rank,
            num_children: response_json[child].num_children,
            selectable: response_json[child].any_assays,
            shown: false,
            selected: false,
            collapsed: true,
          }
        )
      }
    }
    else {
      let msg = await response.text()
      alert(msg);
    }
  },
  methods : {
    toggle(taxon) {
      this.taxons[taxon].shown = true;
      this.taxons[taxon].collapsed = !this.taxons[taxon].collapsed;
      setTimeout(() => {
        this.$root.$emit('bv::toggle::collapse', taxon+'-toggle');
      }, 50);
    },
    select(taxon) {
      if (this.taxons[taxon].selectable) {
        var root = this.$root;
        /* Flip selected variable */
        this.taxons[taxon].selected = !this.taxons[taxon].selected;
        if (this.taxons[taxon].selected) {
          /* Add to selectedDesigns */
          root.$data.selectedDesigns.push([taxon, this.taxons[taxon].name])
        } else {
          /* Remove from selectedDesigns */
          let index = -1;
          for (let i in root.$data.selectedDesigns) {
            if (root.$data.selectedDesigns[i][0] == taxon) {
              index = i;
            }
          }
          if (index > -1) {
            root.$data.selectedDesigns.splice(index, 1);
          }
        }
        /* Resort selectedDesigns by primary key order */
        root.$data.selectedDesigns.sort();
        /* Make call for functions listening */
        root.$emit('designs-update');
      }
    }
  }
}
</script>
