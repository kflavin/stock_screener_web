// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import Router from './routes.js'  // default exports can be imported with any name
import VueResource from 'vue-resource'
import Auth from './plugins/Auth.js'

Vue.use(VueResource);
Vue.use(Auth);

Vue.config.productionTip = false;

// Configure alertify
alertify.defaults.notifier.position = 'top-right';


// Interceptor used to add host to XHR requests, and catch and display any error responses
// handled from vue-resource http object
Vue.http.interceptors.push(function(request, next) {
  if (request.url[0] === '/') {
    // Load the API value from config files
    request.url = process.env.API + request.url;

    // Use interceptors to send back token, if it exists
    var token = Vue.auth.getToken();
    if (token) {
      request.headers.set('Authorization', 'Bearer ' + token)
    }
  }

  next(function(res) {
      if (res.status == 400 || res.status == 401) {
     //   res.body.errors.forEach( function(err) {
     //     alertify(e);
     //   });
       alertify.error(res.body.message);
     }
  });
});

// Navigation guards are being used here to prevent logged in users from seeing login page
// Checks "requiresGuest" property
Router.beforeEach(function(to, from, next) {
  console.log(Vue.auth.loggedIn());

  if (to.matched.some(function(record) {return record.meta.requiresGuest; })
        && Vue.auth.loggedIn()) {
          next({
            path: '/newsfeed'
          });
        } else {
          next(); // always be sure to call next
        }
});

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router: Router,
  template: '<App/>',
  components: { App }
})
