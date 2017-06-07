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

Vue.http.interceptors.push(function(request, next) {
  if (request.url[0] == '/') {
    // Load the API value from config files
    request.url = process.env.API + request.url;
    console.log(process.env.API)
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

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router: Router,
  template: '<App/>',
  components: { App }
})
