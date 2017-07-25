<template>
  <v-container fluid>
    <v-layout>
      <v-flex xs12 sm6 offset-sm1>
      <h4>{{companyName}}</h4>
      <h4>{{this.$route.params.symbol}}</h4>
      <h4>{{sector}}</h4>
      <h4>{{industry}}</h4>
    </v-flex>

    </v-layout>
  </v-container>
</template>

<script>
  export default {
    name: "companies",
    created: function() {
      this.getCompany(this.$route.params.symbol);
    },
    data: function() {
      return {
        companyName: "",
        symbol: "",
        sector: "",
        industry: ""
      }
    },
    props: {
      symbolasdf: {type: String, default: "A"}
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
        })
      }
    }
  }
</script>

<style scoped>
</style>
