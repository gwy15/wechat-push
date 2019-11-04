<template>
  <div class="message-sender">
    <Form
      ref="senderForm"
      style="max-width: 600px; margin:auto"
      :model="formData"
      :rules="ruleMessage"
      label-position="right"
      :label-width="100"
    >
      <FormItem label="openID" prop="openID">
        <Input
          v-model="formData.openID"
          placeholder="Input OpenID for receiver"
        />
      </FormItem>
      <FormItem label="Title" prop="title">
        <Input v-model="formData.title" placeholder="Input title for message" />
      </FormItem>
      <FormItem label="body" prop="body">
        <Input
          v-model="formData.body"
          placeholder="Input body for message (Optional)."
          type="textarea"
          :autosize="{ minRows: 2, maxRows: 10 }"
        />
      </FormItem>
      <FormItem label="url" prop="url">
        <Input
          v-model="formData.url"
          placeholder="Input url for message (Optional)."
        />
      </FormItem>
      <FormItem>
        <Button type="primary" @click="handleSubmit('senderForm')">发送</Button>
        <Button v-if="success" @click="gotoDetail" style="margin-left: 8px">
          查看
        </Button>
      </FormItem>
    </Form>
  </div>
</template>

<script>
import { Form, FormItem, Input, Button } from "view-design";
import axios from "axios";
import { urls } from "@/utils/url";

export default {
  name: "MessageSender",
  components: {
    Form,
    FormItem,
    Input,
    Button
  },
  props: {
    openID: {
      type: String,
      default: ""
    }
  },
  data() {
    return {
      success: false,
      token: "",
      formData: {
        openID: this.openID,
        title: "",
        body: "",
        url: ""
      },
      ruleMessage: {
        openID: [{ required: true, message: "Open ID cannot be empty" }],
        title: [{ required: true, message: "Title cannot be empty" }]
      }
    };
  },
  methods: {
    handleSubmit(formName) {
      const app = this;
      const msg = app.$Message;
      this.$refs[formName].validate(valid => {
        if (!valid) {
          return;
        }

        const data = new FormData();
        data.append("receiver", app.formData.openID);
        data.append("title", app.formData.title);
        data.append("body", app.formData.body);
        data.append("url", app.formData.url);
        const removeLoading = msg.loading({
          content: "Message sending...",
          duration: 0
        });
        axios
          .post(urls.messageUrl(), data)
          .then(function(response) {
            const resp = response.data;
            removeLoading();
            if (resp.success) {
              msg.success("Request success");
              console.log(resp.data);
              app.success = true;
              app.token = resp.data.token;
              console.log(app);
            } else {
              if (resp.msg.includes("40003")) {
                msg.error("Wechat request failed. Check your open ID.");
              } else {
                msg.error("wechat request failed.");
              }
            }
          })
          .catch(function(err) {
            removeLoading();
            msg.error("Network request failed.");
            throw err;
          });
      });
    },
    gotoDetail() {
      this.$router.push({ name: "detail", params: { token: this.token } });
    }
  }
};
</script>

<style scoped>
div.message-sender {
  text-align: center;
}
</style>
