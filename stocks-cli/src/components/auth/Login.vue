<template>
  <v-app>
    <main>
      <v-card class="grey lighten-4 elevation-10">
          <v-card-text>
            <v-container>
              <v-layout>
                <v-flex xs4>
                  <v-subheader>Email</v-subheader>
                </v-flex>
                <v-flex xs4>
                  <v-text-field
                    name="Email"
                    label="Enter your email or username"
                    id="Email"
                    v-model="user.email"
                    @keyup.native.enter="login"
                  ></v-text-field>
                </v-flex>
              </v-layout>
              <v-layout row>
              <v-flex xs4>
                <v-subheader>Password</v-subheader>
              </v-flex>
              <v-flex xs4>
                <v-text-field
                  name="password"
                  label="Enter your password"
                  v-model="user.password"
                  @keyup.native.enter="login"
                ></v-text-field>
                <v-btn v-on:keyup.enter.native="login" @click.native="login" primary dark raised>Login</v-btn>
                <v-btn v-on:keyup.enter.native="login" @click.native="login" dark>Register</v-btn>
                <p class="text-center">
                  Don't have an account?  <router-link to="/auth/register">Sign up!</router-link>
                </p>
              </v-flex>
            </v-layout>
            </v-container>
          </v-card-text>
        </v-card>
  </main>
  </v-app>


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
            this.$store.commit('setCurrentUser', this.user);
            alertify.success("You have logged in!");
            this.$router.push('/');
          }); // catch block is handled in main.js as an interceptor
      },
      logit: function() {
        console.log("button pressed!");
      }
    }
  }
</script>

<style>

</style>
