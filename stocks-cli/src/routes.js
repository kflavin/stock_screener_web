import Vue from 'vue';
import VueRouter from 'vue-router';

import Login from './components/auth/Login.vue';
import Auth from './components/auth/Auth.vue';
import Register from './components/auth/Register.vue';

Vue.use(VueRouter);

var router = new VueRouter({
  // pass routes array to defines routes
  routes: [
    {
      path: "/auth",
      component: Auth,
      redirect: '/auth/login', // redirect to /auth/login if user tries to access parent page
      children: [
        {
          path: "login",
          component: Login
        },
        {
          path: "register",
          component: Register
        }
      ]
    }
  ]
});

export default router;
