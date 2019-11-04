import Vue from "vue";
import VueRouter from "vue-router";
import Home from "../views/Home.vue";

Vue.use(VueRouter);

const routes = [
  {
    path: "/",
    name: "home",
    component: Home
  },
  {
    path: "/sender",
    name: "sender",
    component: () =>
      import(/* webpackChunkName: "sendpage" */ "../views/SendPage.vue")
  },
  {
    path: "/detail/:token",
    name: "detail",
    // route level code-splitting
    // this generates a separate chunk (detail.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () =>
      import(/* webpackChunkName: "detail" */ "../views/Detail.vue")
  }
];

const router = new VueRouter({
  routes,
  mode: "history"
});

export default router;
