<template>
  <v-data-table
    v-bind:headers="headers"
    v-bind:items="items"
    v-bind:search="search"
    class="elevation-1"
  >
    <template slot="items" scope="props">
      <td>{{ props.item.name }}</td>
      <td class="text-xs-right">{{ props.item.symbol }}</td>
    </template>
  </v-data-table>
</template>

<script>

export default {
    name: "listings",
    data: function() {
      return {
        search: '',
        totalItems: 0,
        items: [],
        loading: false,
        pagination: {},
        headers: [
          {
            text: 'Name',
            left: true,
            sortable: true,
            value: 'name'
          },
          { text: 'Ticker', value: 'symbol' }
        ]
      }
    },
    created: function() {
      this.items = []
      this.getCompanies(1)
    },
    methods: {
      getCompanies: function(page) {
        this.$http.get('/api/2.0/company/?count=200').then(function(res) {
          this.items = res.body.companies
          this.totalItems = res.body.companies.length
          console.log("companies retrieved")
          console.log(res)
          console.log(this.items)
          console.log(this.items.length)
        })
      },
    }
}

</script>

<style scoped>
</style>
