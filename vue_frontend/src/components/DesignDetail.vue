<template>
  <div class="designdetail">
   <div
      v-for="taxon in Object.keys(taxons)"
      :key="taxon"
    >
      <h1 :class="taxons[taxon].rank">
        {{ taxons[taxon].name }}
        <a
          :id="taxon+'-arrow'"
          :class="{ collapsed: taxons[taxon].collapsed, 'not-collapsed': !taxons[taxon].collapsed }"
          :href="'#' + taxon + '-toggle'"
          v-if="taxons[taxon].num_children>0"
          v-on:click="toggle(taxon)"
          @click.prevent
        >
          <b-icon-chevron-down class="when-closed" :aria-label="'Expand ' + taxons[taxon].name"/>
          <b-icon-chevron-up class="when-open" :aria-label="'Collapse ' + taxons[taxon].name"/>
        </a>
      </h1>
      <b-collapse :id="taxon + '-toggle'" v-if="taxons[taxon].shown">
        <DesignDetail :parent="taxon"></DesignDetail>
      </b-collapse>
    </div>
  </div>
</template>

<script>
const Cookies = require('js-cookie');
// Needs CSRF for the server to accept the request
const csrfToken = Cookies.get('csrftoken')

export default {
  name: 'DesignDetail',
  props: {
    parent: String
  },
  data() {
    return {
      taxons: {},
    }
  },
  created () {
    this.loadChildren(this.parent)
  },
  methods : {
    async loadChildren () {
      let response = await fetch('/api/taxonrank?parent=' + this.parent.slice(2), {
        headers: {
          "X-CSRFToken": csrfToken
        }
      })
      var parent_dict = this.taxons
      // 'pknull' == primary key null, in reference to the primary key of the parent in the API call
      // if parents[0] != 'pknull' {
      //   for (var parent of parents) {
      //     parent_dict = parent_dict[parent]
      //   }
      // }
      if (response.ok) {
        let response_json = await response.json()
        for (var child in response_json) {
          this.$set(parent_dict,
            "pk" + response_json[child].pk.toString(),
            {
              name: response_json[child].latin_name,
              rank: response_json[child].rank,
              num_children: response_json[child].num_children,
              shown: false,
              collapsed: true
            }
          )
        }
      }
      else {
        let msg = await response.text()
        alert(msg);
      }
    },
    toggle(taxon) {
      this.taxons[taxon].shown = true;
      this.taxons[taxon].collapsed = !this.taxons[taxon].collapsed;
      setTimeout(() => {
        this.$root.$emit('bv::toggle::collapse', taxon+'-toggle')
      }, 50);
    },
    get_sub(sec_keys) {
      // Helper function to get children of taxon
      return sec_keys.filter(item => {
        return !(item in ['name', 'rank', 'num_children', 'shown', 'collapsed']);
      })
    },
  }
}
</script>

<style scoped>
.collapsed .when-open,
.not-collapsed .when-closed {
  display: none !important;
}
.family {
  font-size: 2.4rem;
}
.genus {
  font-size: 2rem;
}
.species {
  font-size: 1.6rem;
}
.subspecies {
  font-size: 1.2rem;
}
</style>
