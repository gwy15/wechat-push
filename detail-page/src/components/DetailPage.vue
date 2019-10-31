<template>
  <div class="detail-page">
    <h2>{{ title }}</h2>
    <p id="created-time">{{ createdTime.fromNow() }}</p>
    <vue-markdown id="body" :source="body"></vue-markdown>
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
      createdTime: moment(),
      url: null
    };
  },
  created: function() {
    const locale =
      window.navigator.userLanguage || window.navigator.language || "zh-CN";
    moment.locale(locale);
  },
  mounted: function() {
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
    const apiUrl = process.env.VUE_APP_MESSAGE_URL + "/" + token;
    axios
      .get(apiUrl)
      .then(function(response) {
        const resp = response.data;
        if (resp.success) {
          const data = resp.data;
          app.title = data.title;
          app.body = data.body;
          app.createdTime = moment.unix(data.created_time);
          app.url = data.url;
        } else {
          app.title = "Request failed.";
          app.body = resp.msg;
        }
      })
      .catch(function() {
        app.title = "Request failed.";
        app.body = "Your network request has failed.";
      });
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
p#created-time {
  text-align: right;
  margin-right: 10pt;
}
#body {
  text-align: left;
  margin: 15px;
}
</style>
