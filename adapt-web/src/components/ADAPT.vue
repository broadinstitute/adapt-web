<template>
  <div class="adapt">
    <h1>{{ msg }}</h1>
    <button @click="count++">
      You clicked me {{ count }} times.
    </button>`

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
      const json = JSON.stringify({
        "single_adapt.adapt.queueArn": "None",
        "single_adapt.adapt.taxid": 64320,
        "single_adapt.adapt.ref_accs": "NC_035889",
        "single_adapt.adapt.segment": "None",
        "single_adapt.adapt.obj": "minimize-guides",
        "single_adapt.adapt.specific": false,
        "single_adapt.adapt.image": "quay.io/broadinstitute/adaptcloud",
        "single_adapt.adapt.rand_sample": 5,
        "single_adapt.adapt.rand_seed": 294
      });
      form.append('workflowUrl', 'https://github.com/broadinstitute/adapt-pipes/blob/master/single_adapt.wdl');
      form.append('workflowInputs', json);
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

      const response = await fetch('http://ec2-54-91-18-102.compute-1.amazonaws.com/api/workflows/v1', {
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
