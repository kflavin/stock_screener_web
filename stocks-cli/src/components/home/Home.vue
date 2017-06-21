<template>
<div>
    <div class="row">
        <div class="col-md-6">
            <ul class="nav nav-pills" role="tablist">
                <li role="presentation" v-bind:class="{active: activeTab == 'home'}"><a v-bind:href="'/#/welcome'" @click="setActiveTab('home')">Home</a></li>
                <li role="presentation" v-bind:class="{active: activeTab == 'listings'}"><a v-bind:href="'/#/listings'" @click="setActiveTab('listings')">Listings</a></li>
                <li role="presentation" v-bind:class="{active: activeTab == 'companies'}"><a v-bind:href="'/#/companies'" @click="setActiveTab('companies')">Companies</a></li>
                <li role="presentation" v-bind:class="{active: activeTab == 'messages'}"><a v-bind:href="'/#/messages'" @click="setActiveTab('messages')">Messages <span class="badge">3</span></a></li>
            </ul>
        </div>

        <div class="col-md-3 col-md-offset-2">
            <ul class="nav nav-pills" role="tablist">
                <li role="presentation"><a href="/#/account">My Account</span></a></li>
                <li role="presentation"><a href="#" @click.prevent="logout">Logout</a></li>
            </ul>
        </div>
    </div>

    <div class="row">
        <router-view></router-view>
    </div>
</div>

</template>

<script>

export default {
    name: "home",
    created: function() {
        console.log("This is the home page")
    },
    data: function() {
      return {
        activeTab: "home"
      }
    },
    methods: {
        logout: function() {
            this.$auth.destroyToken();
            this.$router.push("/auth");
        },
        setActiveTab: function(tab) {
          this.activeTab = tab;
        }
    },
    computed: {
      classObject: function() {
        console.log("computed property");
        console.log(this.$route.path);



        return {
          active: true
        }
      }
    }
}

</script>

<style scoped>
</style>
