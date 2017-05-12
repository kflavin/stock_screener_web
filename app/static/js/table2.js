var axios = require('axios');
//var Paginate = require('vuejs-paginate');

// Vue.component('paginate', Paginate);
// //Vue.component('paginate', VuejsPaginate)

// new Vue({
//   el: '#app',
//   methods: {
//     clickCallback: function(pageNum) {
//       console.log(pageNum)
//     }
//   }
// })

var App = require('./App.vue')
var Paginate = require('vuejs-paginate')
//var Vue = require('vue')
var Vue = require('vue/dist/vue')

Vue.component('paginate', Paginate)

new Vue({
  el: '#app',
  template: '<App/>',
  components: { App },
  render: function(createElement) {
    return createElement(App)
  }
})

// register the grid component
Vue.component('demo-grid', {
  template: '#grid-template',
  props: {
    blah: Array,
    columns: Array,
    filterKey: String
  },
  delimiters: ['((', '))'],
  data: function () {
    var sortOrders = {}
    this.columns.forEach(function (key) {
      sortOrders[key] = 1
    })
    return {
      sortKey: '',
      sortOrders: sortOrders
    }
  },
  computed: {
    filteredData: function () {
      var sortKey = this.sortKey
      var filterKey = this.filterKey && this.filterKey.toLowerCase()
      var order = this.sortOrders[sortKey] || 1
      var data = this.blah

      if (filterKey) {
        data = data.filter(function (row) {
          return Object.keys(row).some(function (key) {
            return String(row[key]).toLowerCase().indexOf(filterKey) > -1
          })
        })
      }
      if (sortKey) {
        data = data.slice().sort(function (a, b) {
          a = a[sortKey]
          b = b[sortKey]
          return (a === b ? 0 : a > b ? 1 : -1) * order
        })
      }
      return data
    }
  },
  filters: {
    capitalize: function (str) {
      return str.charAt(0).toUpperCase() + str.slice(1)
    }
  },
  methods: {
    sortBy: function (key) {
      this.sortKey = key
      this.sortOrders[key] = this.sortOrders[key] * -1
    }
  }
})

// Vue.component('child', {
//   template: '<div>a custom component!</div>'
// });

// var one = new Vue({
//   el: '#one'
// })

// bootstrap the demo
var demo = new Vue({
  el: '#demo',
  data: {
    searchQuery: '',
    gridColumns: ['id', 'industry', 'name', 'sector', 'sic_code', 'symbol'],
    gridData: [],
    someText: "hi"
  },
  components: {
    child: {
      props: ['myMessage'],
      template: '<div>{{myMessage}}'
    }
  },
  created: function() {
    this.fetchCompanies();
  },
  methods: {
    fetchCompanies: function() {
      axios.get('http://127.0.0.1:5000/api/1.0/company/')
        .then(function(response) {
          //this.gridData = [{name: 'Joe', power: "1000"}];
          this.gridData = response.data.companies;
          console.log("Your data");
          console.log(this.gridData);
        }.bind(this))
        .catch(function(error) {
          console.log("error");
        })
    }
  }
})
