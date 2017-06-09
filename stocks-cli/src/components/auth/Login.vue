<template>
  <div>
    <h3 class="text-center">Login</h3>
    <input type="text" class="form-control m-b-15" placeholder="Email"
      v-model="user.email">
    <input type="password" class="form-control m-b-15" placeholder="Password"
      v-model="user.password">
    <hr>
    <button class="btn btn-lg btn-primary btn-block m-b-15"
      v-on:click="login">Sign in</button>

    <p class="text-center">
      Don't have an account?  <router-link to="/auth/register">Sign up!</router-link>
    </p>
  </div>
</template>

<script>
  export default {
    name: "login",
    data: function() {
      return {
        user: {
          "email": "",
          "password": ""
        }
      }
    },
    methods: {
      login: function() {
        this.$http.post("/api/2.0/auth/login", this.user)
          .then(function(res) {
            this.$auth.setToken(res.body.token, Date.now() + 14400000);  // ms in 4 hours
            alertify.success("You have logged in!");
            this.$router.push('/newsfeed');
          }); // catch block is handled in main.js as an interceptor
      }
    }
  }
</script>

<style>

</style>
