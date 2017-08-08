import Vue from 'vue';
import VueRouter from 'vue-router';

import Login from './components/auth/Login.vue';
import Auth from './components/auth/Auth.vue';
import Register from './components/auth/Register.vue';
import Home from './components/home/Home.vue';
import Welcome from './components/home/Welcome.vue';
import Listings from './components/home/Listings.vue';
import Companies from './components/home/Companies.vue';
import Messages from './components/home/Messages.vue';
import Tab1 from './components/home/Tab1.vue';

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
          component: Login,
          meta: { requiresGuest: true }
        },
        {
          path: "register",
          component: Register,
          meta: { requiresGuest: true }
        }
      ]
    },
    {
      path: "/",
      component: Home,
      redirect: 'welcome',
      children: [
        {
          path: "welcome",
          component: Welcome,
          meta: { requiresAuth: true }
        },
        {
          path: "listings",
          component: Listings,
          meta: { requiresAuth: true }
        },
        {
          path: "company/:symbol",
          component: Companies,
          meta: { requiresAuth: true },
          children: [
            {
              path: "details",
              component: Tab1,
              meta: { requiresAuth: true }
            },
            {
              path: "indicators",
              component: Tab1,
              meta: { requiresAuth: true }
            },
            {
              path: "news",
              component: Tab1,
              meta: { requiresAuth: true }
            }
          ]
        },
        {
          path: "messages",
          component: Messages,
          meta: { requiresAuth: true }
        }
      ]
    }
  ]
});

export default router;
