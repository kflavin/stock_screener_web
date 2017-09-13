_ = require('lodash');

new Vue({
  // -------------
  // APP CONTAINER
  // -------------
  el: '#app',
  
  // --------
  // RAW DATA
  // --------
  data: {
    tableColumns: [
      {
        title: 'Name',
        field: 'name'
      }, {
        title: 'Company',
        field: 'company.name'
      }, {
        title: 'Website',
        field: 'website'
      }
    ],
    users: [],
    filterQuery: '',
    orderByField: 'name',
    fetchError: false
  },

  delimiters: ['((', '))'],
  
  // ------------
  // DERIVED DATA
  // ------------
  computed: {
    filteredUsers: function () {
      var vm = this
      return _.orderBy(
        vm.users.filter(function (user) {
          var regex = new RegExp(vm.filterQuery, 'i')
          return (
            regex.test(user.name) ||
            regex.test(user.company.name) ||
            regex.test(user.website)
          )
        }), 
        vm.orderByField
      )
    },
    statusMessage: function () {
      if (this.fetchError) {
        return 'There was a problem fetching the users. JSONPlaceholder might be down.'
      }
      if (this.users.length) {
        if (!this.filteredUsers.length) {
          return 'Sorry, no matching users were found.'
        }
      } else {
        return 'Loading...'
      }
    }
  },
  
  // ---------------
  // LIFECYCLE HOOKS
  // ---------------
  created: function () {
    this.fetchUsers()
  },

  // --------------
  // SCOPED METHODS
  // --------------
  methods: {
    fetchUsers: function () {
      var vm = this
      vm.users = []
      vm.fetchError = false
      fetch('http://localhost:5000/api/1.0/company/')
        .then(function (response) { console.log("starting response.."); return response.json() })
        .then(function (users) { console.log("have users"); console.log(users); vm.users = users.companies; console.log(vm.users); })
        .catch(function (error) { console.log("there was an error"); console.log(error); vm.fetchError = true })
    },
    getField: function (object, field) {
      return _.at(object, field)[0]
    } 
  }
})