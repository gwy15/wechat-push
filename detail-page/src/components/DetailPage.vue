<template>
  <div class="detail-page">
    <h2>{{ title }}</h2>
    <p>{{ createdTime.fromNow() }}</p>
    <vue-markdown :source="body"></vue-markdown>
  </div>
</template>

<script>
import axios from "axios";
import VueMarkdown from "vue-markdown";
import moment from "moment";

export default {
  name: "DetailPage",
  components: {
    VueMarkdown
  },
  data: function() {
    return {
      title: "Loading",
      body: "loading data from server...",
      createdTime: moment()
    };
  },
  created: function() {
    const locale =
      window.navigator.userLanguage || window.navigator.language || "zh-CN";
    console.log("Use locale: " + locale);
    moment.locale(locale);
  },
  mounted: function() {
    console.log("mounted");
    const app = this;
    // parse url param
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get("token", null);
    if (token == null) {
      app.title = "Token not found";
      app.body = "Token not found. Don't visit this page directly.";
      return;
    }
    // api request
    const apiUrl = process.env.VUE_APP_DETAIL_URL + "?token=" + token;
    axios
      .get(apiUrl)
      .then(function(response) {
        app.title = response.title;
        app.body = response.body;
        app.createdTime = moment.unix(response.createdTime); // TODO:
      })
      .catch(function(err) {
        console.log(err);
        app.title = "Request failed.";
        app.body = "Your network request has failed.";
      });
    console.log("app created");
  }
};
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
