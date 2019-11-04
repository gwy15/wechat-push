<template>
  <div class="home-page">
    <h2 v-text="title"></h2>

    <div v-if="scene">
      <div>
        <img :src="scene.QRUrl" id="qr-code" />
      </div>
      <p v-text="expireTime"></p>
    </div>
    <h3 v-else v-text="openID"></h3>
    <div v-if="success">
      <MessageSender :openID="openID" />
    </div>
  </div>
</template>

<script>
import axios from "axios";
import moment from "moment";
import { urls } from "@/utils/url";
import MessageSender from "@/components/MessageSender";

export default {
  name: "home",
  components: {
    MessageSender
  },
  data: function() {
    return {
      title: "Scan QR code to register",
      scene: null,
      openID: "Loading...",
      expireAt: moment(),
      success: false
    };
  },
  mounted: function() {
    const app = this;
    axios
      .post(urls.sceneUrl())
      .then(function(response) {
        const resp = response.data;
        if (resp.success) {
          app.scene = resp.data;
          // begin polling
          app.expireAt = moment.unix(app.scene.expire_at);
          window.setTimeout(app.checkScene, 1000);
        } else {
          app.title = "Wechat Request failed.";
        }
      })
      .catch(function() {
        app.title = "Request failed.";
        app.openID =
          "Try refresh or open developer console if you known what it means.";
      });
  },
  computed: {
    expireTime: function() {
      moment.locale("zh-CN");
      const t = moment.unix(this.scene.expire_at).fromNow();
      return t + " 过期";
    }
  },
  methods: {
    checkScene: function() {
      const app = this;
      axios
        .get(urls.sceneUrl(app.scene.scene_id))
        .then(function(response) {
          const resp = response.data;
          app.success = true;
          app.title = "你的 OpenID 为：";
          app.scene = null;
          app.openID = resp.data.openID;
        })
        .catch(function(err) {
          if (err.response.status == 404) {
            // not yet.
            if (moment() > app.expireAt) {
              app.title = "超时，请刷新重试";
              app.scene = null;
              app.openID = "";
            } else {
              window.setTimeout(app.checkScene, 1000);
            }
          } else {
            app.title = "Request failed.";
            app.scene = null;
            app.openID = err.response.data;
          }
        });
    }
  }
};
</script>

<style scoped>
img#qr-code {
  max-width: 300px;
}
</style>
