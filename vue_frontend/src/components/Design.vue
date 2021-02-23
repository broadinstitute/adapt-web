<template>
  <transition appear name="fade">
    <div class="design">
      <div
        v-for="family in families"
        :key="family.taxon"
      >
        <a
          v-b-toggle
          :href="'#fam' + family.taxon + '-toggle'"
          @click.prevent
        >
          <h1>
            {{ family.name }} ({{ family.taxon }}) <b-icon-chevron-down class="when-closed"/><b-icon-chevron-up class="when-open"/>
          </h1>
        </a>
        <b-collapse :id="'fam' + family.taxon + '-toggle'">
          <h2>insert genus here</h2>
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
      families: [],
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
          this.families.push({
            taxon: response_json[family].taxon,
            name: response_json[family].latin_name,
          })
        }
      }
      else {
        let msg = await response.text()
        alert(msg);
      }
    },
    async loadGenus (family) {
      let response = await fetch('/api/genus?family=' + family, {
        headers: {
          "X-CSRFToken": csrfToken
        }
      })
      if (response.ok) {
        let response_json = await response.json()
        for (var genus in response_json) {
          this.viruses[family][genus.taxon] = {
            name: genus.latin_name,
          }
        }
      }
      else {
        let msg = await response.text()
        alert(msg);
      }
    },
    async loadSpecies (family, genus) {
      let response = await fetch('/api/species?genus=' + genus, {
        headers: {
          "X-CSRFToken": csrfToken
        }
      })
      if (response.ok) {
        let response_json = await response.json()
        for (var species in response_json) {
          this.viruses[family][genus][species.taxon] = {
            name: species.latin_name,
          }
        }
      }
      else {
        let msg = await response.text()
        alert(msg);
      }
    },
    async loadSubspecies (family, genus, species) {
      let response = await fetch('/api/subspecies?species=' + species, {
        headers: {
          "X-CSRFToken": csrfToken
        }
      })
      if (response.ok) {
        let response_json = await response.json()
        for (var subspecies in response_json) {
          this.viruses[family][genus][species][subspecies.taxon] = {
            name: subspecies.latin_name,
          }
        }
      }
      else {
        let msg = await response.text()
        alert(msg);
      }
    }
  }
}
</script>

<style scoped>
.collapsed .when-open,
.not-collapsed .when-closed {
  display: none !important;
}
</style>
