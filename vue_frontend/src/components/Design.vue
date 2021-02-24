<template>
  <transition appear name="fade">
    <div class="design">
      <div
        v-for="family in Object.keys(families)"
        :key="family"
      >
        <h1>
          {{ families[family].name }} ({{ family.slice(2) }})
          <a
            v-b-toggle
            :href="'#' + family + '-toggle'"
            v-on:click.once="loadGenus(family)"
            @click.prevent
          >
            <b-icon-chevron-down class="when-closed" :aria-label="'Expand ' + families[family].name"/>
            <b-icon-chevron-up class="when-open" :aria-label="'Collapse ' + families[family].name"/>
          </a>
        </h1>
        <b-collapse :id="family + '-toggle'">
          <div
            v-for="genus in get_sub(Object.keys(families[family]))"
            :key="genus"
          >
            <h2>
              {{ families[family][genus].name }} ({{ genus.slice(2) }})
              <a
                v-b-toggle
                :href="'#' + genus + '-toggle'"
                v-on:click.once="loadSpecies(family, genus)"
                @click.prevent
              >
                <b-icon-chevron-down class="when-closed" :aria-label="'Expand ' + families[family][genus].name"/>
                <b-icon-chevron-up class="when-open" :aria-label="'Collapse ' + families[family][genus].name"/>
              </a>
            </h2>
            <b-collapse :id="genus + '-toggle'">
              <div
                v-for="species in get_sub(Object.keys(families[family][genus]))"
                :key="species"
              >
                <h3>
                  {{ families[family][genus][species].name }} ({{ species.slice(2) }})
                  <a
                    v-b-toggle
                    :href="'#' + species + '-toggle'"
                    v-on:click.once="loadSubspecies(family, genus, species)"
                    @click.prevent
                  >
                    <b-icon-chevron-down class="when-closed" :aria-label="'Expand ' + families[family][genus][species].name"/>
                    <b-icon-chevron-up class="when-open" :aria-label="'Collapse ' + families[family][genus][species].name"/>
                  </a>
                </h3>
                <b-collapse :id="species + '-toggle'">
                  <div
                    v-for="subspecies in get_sub(Object.keys(families[family][genus][species]))"
                    :key="subspecies"
                  >
                    <h4>
                      {{ families[family][genus][species][subspecies].name }} ({{ subspecies.slice(2) }})
                    </h4>
                  </div>
                </b-collapse>
              </div>
            </b-collapse>
          </div>
        </b-collapse>
      </div>
    </div>
  </transition>
</template>

<script>
const Cookies = require('js-cookie');
// Needs CSRF for the server to accept the request
const csrfToken = Cookies.get('csrftoken')

export default {
  name: 'Design',
  data() {
    return {
      families: {},
    }
  },
  created () {
    this.loadFamilies()
  },
  methods : {
    async loadFamilies () {
      let response = await fetch('/api/family/', {
        headers: {
          "X-CSRFToken": csrfToken
        }
      })
      if (response.ok) {
        let response_json = await response.json()
        for (var family in response_json) {
          this.$set(this.families,
            "tx" + response_json[family].taxon.toString(),
            {name: response_json[family].latin_name}
          )
        }
      }
      else {
        let msg = await response.text()
        alert(msg);
      }
    },
    async loadGenus (family) {
      let response = await fetch('/api/genus?family=' + family.slice(2), {
        headers: {
          "X-CSRFToken": csrfToken
        }
      })
      if (response.ok) {
        let response_json = await response.json()
        for (var genus in response_json) {
          this.$set(this.families[family],
            "tx" + response_json[genus].taxon.toString(),
            {name: response_json[genus].latin_name}
          )
        }
      }
      else {
        let msg = await response.text()
        alert(msg);
      }
    },
    async loadSpecies (family, genus) {
      let response = await fetch('/api/species?genus=' + genus.slice(2), {
        headers: {
          "X-CSRFToken": csrfToken
        }
      })
      if (response.ok) {
        let response_json = await response.json()
        for (var species in response_json) {
          this.$set(this.families[family][genus],
            "tx" + response_json[species].taxon.toString(),
            {name: response_json[species].latin_name}
          )
        }
      }
      else {
        let msg = await response.text()
        alert(msg);
      }
    },
    async loadSubspecies (family, genus, species) {
      let response = await fetch('/api/subspecies?species=' + species.slice(2), {
        headers: {
          "X-CSRFToken": csrfToken
        }
      })
      if (response.ok) {
        let response_json = await response.json()
        for (var subspecies in response_json) {
          this.$set(this.families[family][genus][species],
            "tx" + response_json[subspecies].taxon.toString(),
            {name: response_json[subspecies].latin_name}
          )
        }
      }
      else {
        let msg = await response.text()
        alert(msg);
      }
    },
    get_sub(sec_keys) {
      // Helper function to get children of taxon
      return sec_keys.filter(item => {
        return item != 'name';
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
</style>
