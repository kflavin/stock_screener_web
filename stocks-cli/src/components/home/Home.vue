<template>
<v-app>
    <v-navigation-drawer
    persistent
    :mini-variant="miniVariant"
    :clipped="clipped"
    v-model="drawer">
    <v-list>
      <v-list-item
        v-for="(item, i) in items"
        :key="i"
        @click="navigate(item.title, item.url)"
      >
        <v-list-tile value="true">
          <v-list-tile-action>
            <v-icon light v-html="item.icon"></v-icon>
          </v-list-tile-action>
          <v-list-tile-content>
            <v-list-tile-title v-text="item.title"></v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>
      </v-list-item>
    </v-list>
    </v-navigation-drawer>
    <v-toolbar dark class="primary">
      <v-toolbar-side-icon @click.native.stop="drawer = !drawer"></v-toolbar-side-icon>
      <v-toolbar-title class="white--text">Stock Screener</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn icon>
        <v-icon>assessment</v-icon>
      </v-btn>
      <v-btn icon>
        <v-icon>apps</v-icon>
      </v-btn>
      <v-btn icon>
        <v-icon>refresh</v-icon>
      </v-btn>
      <v-btn icon>
        <v-icon>more_vert</v-icon>
      </v-btn>
    </v-toolbar>
    <main>
          <transition name="fade">
            <router-view></router-view>
          </transition>
    </main>
</v-app>
</template>

<script>

export default {
    name: "home",
    created: function() {
        console.log("This is the home page")
    },
    data: function() {
      return {
        activeTab: "home",
        clipped: false,
        drawer: false,
        items: [
          { icon: 'home', title: 'Home', url:'/welcome'  },
          { icon: 'view_list', title: 'Listings', url: '/listings' },
          { icon: 'work', title: 'Companies', url: '/companies' },
          { icon: 'message', title: 'Messages', url: '/messages' },
          { icon: 'close', title: 'Logout', url: '/messages' },
        ],
        miniVariant: false,
      }
    },
    methods: {
        logout: function() {
            this.$auth.destroyToken();
            this.$router.push("/auth");
        },
        setActiveTab: function(tab) {
          this.activeTab = tab;
        },
        navigate: function(action, url) {
          if (action === "Logout") {
            this.logout();
          } else {
            this.$router.push(url);
          }
        }
    },
    computed: {
      classObject: function() {
        console.log("computed property");
        console.log(this.$route.path);

        return {
          active: true
        }
      },
      user: function() {
        return this.$store.state.currentUser;
      }

    }
}

</script>

<style scoped>
</style>
