<template>
  <div class="home-page">
    <h2 v-text="title"></h2>

    <div v-if="scene">
      <div>
        <img :src="scene.QRUrl" id="qr-code" />
      </div>
      <p v-text="expireTime"></p>
      <el-button type="success" round @click="jump2Wechat">手机点击</el-button>
    </div>
    <h3 v-else v-text="openID"></h3>
  </div>
</template>

<script>
import axios from "axios";
import moment from "moment";

export default {
  name: "home",
  data: function() {
    return {
      title: "Scan QR code to register",
      scene: null,
      openID: "Loading...",
      expireAt: moment()
    };
  },
  mounted: function() {
    const app = this;
    axios
      .post(process.env.VUE_APP_SCENE_URL)
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
    jump2Wechat: function() {
      window.open(this.scene.decodedUrl, "_blank");
    },
    checkScene: function() {
      const app = this;
      axios
        .get(process.env.VUE_APP_SCENE_URL + "/" + app.scene.scene_id)
        .then(function(response) {
          const resp = response.data;
          app.title = "你的 OpenID 为：";
          app.scene = null;
          app.openID = resp.data.openID;
        })
        .catch(function() {
          // not yet.
          if (moment() > app.expireAt) {
            app.title = "超时，请刷新重试";
            app.scene = null;
            app.openID = "";
          } else {
            window.setTimeout(app.checkScene, 1000);
          }
        });
    }
  }
};
</script>

<style scoped>
img#qr-code {
  max-width: 400px;
}
</style>
