<template>
  <div>
    <h4 class="ml-3 mt-3">{{this.companyName}} ({{this.symbol}})</h4>
    <v-tabs dark v-model="active">
      <v-tabs-bar slot="activators" class="blue lighten-3">
        <v-tabs-item
          v-for="item in items"
          :key="item"
          :href="'#'+item.router"
          ripple
        >
          {{ item.title }}
        </v-tabs-item>
        <v-tabs-slider class="blue darken-3"></v-tabs-slider>
      </v-tabs-bar>
      <v-tabs-content
        key="details"
        id="details"
      >
        <v-card>
          <v-card-text>details</v-card-text>
        </v-card>
      </v-tabs-content>
      <v-tabs-content
        key="indicators"
        id="indicators"
      >
        <v-card>
          <v-card-text>
            ROE: {{indicators.roe}} <br />
            EV/EBITDA: {{indicators.ev2ebitda}} <br />
            Free Cash Flow: {{indicators.fcf}} <br />
            <br />Cleaned versions<br />
            ROE: {{roeClean}} <br />
            EV/EBITDA: {{ev2ebitdaClean}} <br />
            Free Cash Flow: {{fcfClean}} <br />


          </v-card-text>
        </v-card>
      </v-tabs-content>
      <v-tabs-content
        key="research"
        id="research"
      >
        <v-card>
          <v-card-text>
          <a :href="'https://whalewisdom.com/stock/'+this.symbol">Whale Wisdom</a>
          </v-card-text>
        </v-card>
      </v-tabs-content>
      <v-tabs-content
        key="news"
        id="news"
      >
        <v-card>
          <v-card-text>Items in the news</v-card-text>
        </v-card>
      </v-tabs-content>
    </v-tabs>
  </div>
</template>

<script>
  export default {
    name: "companies",
    created: function() {
      this.getCompany(this.$route.params.symbol);
      // this.getIndicators(this.id);
    },
    data: function() {
      return {
        tabs: ['tab-1', 'tab-2', 'tab-3'],
        active: null,
        text: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
        companyName: "",
        symbol: "",
        sector: "",
        industry: "",
        id: "",
        indicators: {},
        items: [ {item: '1', title: "Company Details", router: "details"},
                {item: '2', title: "Indicators", router: "indicators"},
                {item: '3', title: "Research", router: "research"},
                {item: '4', title: "In the News", router: "news"}],
        // tabs: ["details", "indicators", "news"],
        // tabData: {
        //   details: {
        //     title: "Company details",
        //     href: "details"
        //   },
        //   indicators: {
        //     title: "Indicators",
        //     href: "indicators"
        //   },
        //   details: {
        //     title: "In the News",
        //     href: "news"
        //   }
        // },
        // active: null
      }
    },
    computed: {
      fcfClean: function() {
        if (this.indicators.fcf == -999999999999.99) {
          console.log("we have an invalid value, let's clean it!");
          return "Not available";
        } else {
          return this.indicators.fcf;
        }
      },
      roeClean: function() {
        if (this.indicators.roe == -999999999999.99) {
          console.log("we have an invalid value, let's clean it!");
          return "Not available";
        } else {
          return this.indicators.roe;
        }
      },
      ev2ebitdaClean: function() {
        if (this.indicators.ev2ebitda == -999999999999.99) {
          console.log("we have an invalid value, let's clean it!");
          return "Not available";
        } else {
          return this.indicators.ev2ebitda;
        }
      }
    },
    watch: {
      id: function(id) {
        console.log("watch triggered with id: ");
        console.log(id);
        this.$http.get('/indicators/' + id).then(function(res) {
          console.log("Received indicators:");
          console.log(res.body);
          this.indicators = res.body.indicators;
          // this.fcf = res.body.indicators.fcf;
          // this.roe = res.body.indicators.roe;
          // this.ev2ebitda = res.body.indicators.ev2ebitda;

        });
      }
    },
    methods: {
      getCompany: function(symbol) {
        console.log("getting company " + symbol)
        this.$http.get('/company/' + symbol).then(function(res) {
          console.log(res.body);
          this.companyName = res.body.name;
          this.symbol = res.body.symbol;
          this.sector = res.body.sector;
          this.industry = res.body.industry;
          this.id = res.body.id;
        });
      },
      getIndicators: function(companyId) {
        console.log("getting indicators " + id);
        this.$http.get('/indicators/' + id).then(function(res) {
          console.log(res.body);

        })
      },
      next: function() {
        console.log("actives");
        console.log(this.active);

        // this.tabs.forEach(function(key, value) {
        //   if (key.title.indexOf(this.active))
        //   console.log("key "+ key + " and value" + value);
        // })

        // this.active=this.tabs[2].href;

        this.active = this.tabs[(this.tabs.indexOf(this.active) + 1 ) % this.tabs.length]
        console.log(this.active);
      }
    }
  }
</script>

<style scoped>
</style>
