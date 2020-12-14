<template>
  <div class="adapt">
    <h1>{{ msg }}</h1>
    <button @click="count++">
      You clicked me {{ count }} times.
    </button>`

        <!-- our signup form ===================== -->
    <form id="run-form">
      <div class="field">
        <label class="label">cromwell_id</label>
        <input type="text" class="input" name="cromwell_id">
      </div>

      <!-- name -->
      <div class="field">
        <label class="label">taxid</label>
        <input type="number" class="input" name="taxid">
      </div>

      <!-- email -->
      <div class="field">
        <label class="label">ref_accs</label>
        <input type="text" class="input" name="ref_accs">
      </div>

      <!-- submit button -->
      <div class="field has-text-right">
        <button type="submit" class="button is-danger">Submit</button>
      </div>
    </form>

    <button @click="adapt_run">Run ADAPT on test example</button>
    <h3>Objectives</h3>
    <input type="checkbox" id="max_act" value="maximum_activity" v-model="objs">
    <label for="max_act">Maximum Activity</label>
    <br>
    <input type="checkbox" id="min_guide" value="minimum_guides" v-model="objs">
    <label for="min_guide">Minimum Guides</label>
    <br>
    <span>Picked: {{ objs }}</span>

  </div>
</template>

<script>
// const axios = require("axios");
const FormData = require('form-data');
// const https = require('https');

// const runForm = document.getElementById('run-form');
// const cromwell_idInput  = signupForm.querySelector('input[name=cromwell_id]');
// const taxidInput = signupForm.querySelector('input[name=taxid]');
// const ref_accsInput = signupForm.querySelector('input[name=ref_accs]');
// runForm.addEventListener('submit', processRunForm);


export default {
  name: 'ADAPT',
  props: {
    msg: String
  },
  data () {
    return {
      count: 0,
      name: 'ADAPT',
      objs : []
    }
  },
  methods: {
    async adapt_run(event) {
      const form = new FormData();
      form.append("cromwell_id", "9999-9999-9999-9999")
      form.append("taxid", 99999)
      form.append("ref_accs", "NC_999999")


      // const json = JSON.stringify({
      //   "cromwell_id": "9999-9999-9999-9999",
      //   "taxid": 99999,
      //   "ref_accs": "NC_999999"
      //   // "single_adapt.adapt.queueArn": "None",
      //   // "single_adapt.adapt.taxid": 64320,
      //   // "single_adapt.adapt.ref_accs": "NC_035889",
      //   // "single_adapt.adapt.segment": "None",
      //   // "single_adapt.adapt.obj": "minimize-guides",
      //   // "single_adapt.adapt.specific": false,
      //   // "single_adapt.adapt.image": "quay.io/broadinstitute/adaptcloud",
      //   // "single_adapt.adapt.rand_sample": 5,
      //   // "single_adapt.adapt.rand_seed": 294
      // });
      // form.append('workflowUrl', 'https://github.com/broadinstitute/adapt-pipes/blob/master/single_adapt.wdl');
      // form.append('workflowInputs', json);
      // const agent = new https.Agent({  
      //   rejectUnauthorized: false
      // });

      // var xhr = new XMLHttpRequest();
      // xhr.withCredentials = true;

      // xhr.addEventListener("readystatechange", function () {
      //   if (this.readyState === 4) {
      //     console.log(this.responseText);
      //   }
      // });

      // xhr.open("POST", "https://connect.stripe.com/oauth/token");
      // xhr.setRequestHeader("content-type", "application/x-www-form-urlencoded");
      // xhr.setRequestHeader("cache-control", "no-cache");

      // xhr.send(form);

      const response = await fetch('/api/adaptruns', {
        method: 'post',
        body: form,
      })
      const data = response.json()
      // const { data } = await axios.post("https://ec2-54-91-18-102.compute-1.amazonaws.com/api/workflows/v1", form, {
      //   headers: {'Content-Type': 'multipart/form-data'},
      //   httpsAgent: agent
      // })
      // `this` inside methods points to the current active instance
      alert('Job submitted ' + data.name + '!')
      // `event` is the native DOM event
      if (event) {
        alert(event.target.tagName)
      }
    },
    processSignupForm(e) {
      e.preventDefault();

      // form processing here
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
