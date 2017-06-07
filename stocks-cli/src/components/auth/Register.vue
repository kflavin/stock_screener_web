<template>
  <div>
    <h3 class="text-center">Register</h3>
    <input type="email" class="form-control m-b-15" placeholder="Email Address"
      v-model="user.email">
    <input type="password" class="form-control m-b-15" placeholder="Password"
      v-model="user.password">
    <hr>
    <button class="btn btn-lg btn-primary btn-block m-b-15"
      v-on:click="register">Register</button>

    <p class="text-center">
      Don't have an account?  <router-link to="/auth/login">Login!</router-link>
    </p>
  </div>
</template>

<script>
  export default {
    name: "register",
    data: function() {
      return {
        user: {
          email: "",
          password: ""
        }
      }
    },
    methods: {
        register: function() {
          this.$http.post("/api/2.0/auth/register", this.user)
            .then(function(res) {
                // send a success message, then redirect to the login page
                alertify.success("You have registered.  Please login.");
                this.$router.push('/auth/login');
            }); // catch block is handled in main.js as an interceptor
        }
    }
  }
</script>

<style>
</style>
