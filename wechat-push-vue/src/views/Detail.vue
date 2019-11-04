<template>
  <div class="detail">
    <h2>{{ title }}</h2>
    <p id="created-time">{{ createdTime.fromNow() }}</p>
    <div id="body" v-html="compiledMarkdown"></div>

    <div v-if="url" id="url">
      <a :href="url">查看链接</a>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import marked from "marked";
import moment from "moment";
import { urls } from "@/utils/url";

export default {
  name: "DetailPage",
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
    const token = app.$route.params.token;
    if (token == null) {
      app.title = "Token not found";
      app.body = "Token not found. Don't visit this page directly.";
      return;
    }
    // api request
    const apiUrl = urls.messageUrl(token);
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
      .catch(function(err) {
        if (err.response.status == 404) {
          app.title = "Token not found.";
          app.body = err.response.data;
        } else {
          app.title = "Request failed.";
          app.body = "Your network request has failed.";
        }
      });
  },
  computed: {
    compiledMarkdown: function() {
      return marked(this.body);
    }
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
div.detail {
  max-width: 600px;
  margin: auto;
  padding-left: 10px;
  padding-right: 10px;
}

p#created-time {
  text-align: right;
}
#body {
  text-align: left;
}
div#url {
  text-align: left;
}
</style>
