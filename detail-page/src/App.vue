<template>
  <div id="app">
    <DetailPage />
  </div>
  <!-- TODO: footer -->
</template>

<script>
import DetailPage from "./components/DetailPage.vue";

export default {
  name: "app",
  components: {
    DetailPage
  }
};
</script>

<style>
#app {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
