<template>
  <div id="app" class="container">
    <h1>User Management</h1>
    <div class="mb-3">
      <input type="file" @change="uploadCSV" />
    </div>
    <div class="mb-3">
      <input type="text" v-model="search" placeholder="Search by name, email, or department" class="form-control" />
    </div>
    <div class="mb-3">
      <select v-model="selectedDepartment" @change="filterUsers" class="form-control">
        <option value="">All Departments</option>
        <option v-for="department in departments" :key="department" :value="department">{{ department }}</option>
      </select>
    </div>
    <div class="mb-3">
      <button @click="showGroupModal = true" class="btn btn-primary" :disabled="selectedUsers.length === 0">Manage Groups</button>
      <button @click="exportCSV" class="btn btn-success ml-2">Export CSV</button>
    </div>
    <table class="table">
      <thead>
        <tr>
          <th><input type="checkbox" v-model="selectAll" @change="toggleSelectAll" /></th>
          <th @click="sortUsers('firstname')">First Name</th>
          <th @click="sortUsers('lastname')">Last Name</th>
          <th @click="sortUsers('email')">Email</th>
          <th @click="sortUsers('departments')">Departments</th>
          <th @click="sortUsers('groups')">Groups</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in paginatedUsers" :key="user.email">
          <td><input type="checkbox" v-model="selectedUsers" :value="user" /></td>
          <td>{{ user.firstname }}</td>
          <td>{{ user.lastname }}</td>
          <td>{{ user.email }}</td>
          <td>{{ user.departments }}</td>
          <td>{{ user.groups }}</td>
        </tr>
      </tbody>
    </table>
    <nav aria-label="Page navigation">
      <ul class="pagination justify-content-center">
        <li class="page-item" :class="{ disabled: currentPage === 1 }">
          <a class="page-link" href="#" @click.prevent="changePage(currentPage - 1)">Previous</a>
        </li>
        <li v-for="page in visiblePages" :key="page" class="page-item" :class="{ active: currentPage === page }">
          <a class="page-link" href="#" @click.prevent="changePage(page)">{{ page }}</a>
        </li>
        <li class="page-item" :class="{ disabled: currentPage === totalPages }">
          <a class="page-link" href="#" @click.prevent="changePage(currentPage + 1)">Next</a>
        </li>
      </ul>
    </nav>

    <!-- Group Management Modal -->
    <div v-if="showGroupModal" class="modal" tabindex="-1" role="dialog" style="display: block;">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Manage Groups</h5>
            <button type="button" class="close" @click="showGroupModal = false">
              <span>&times;</span>
            </button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>Add Groups:</label>
              <select v-model="groupsToAdd" multiple class="form-control">
                <option v-for="group in availableGroups" :key="group" :value="group">{{ group }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>New Group:</label>
              <input v-model="newGroup" class="form-control" placeholder="Enter new group name" />
              <button @click="addNewGroup" class="btn btn-secondary mt-2">Add New Group</button>
            </div>
            <div class="form-group">
              <label>Remove Groups:</label>
              <select v-model="groupsToRemove" multiple class="form-control">
                <option v-for="group in currentGroups" :key="group" :value="group">{{ group }}</option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showGroupModal = false">Close</button>
            <button type="button" class="btn btn-primary" @click="updateGroups">Save changes</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import debounce from 'lodash/debounce';

export default {
  name: 'App',
  data() {
    return {
      users: [],
      search: '',
      selectedDepartment: '',
      departments: [],
      currentPage: 1,
      itemsPerPage: 10,
      selectedUsers: [],
      selectAll: false,
      showGroupModal: false,
      groupsToAdd: [],
      groupsToRemove: [],
      newGroup: '',
      availableGroups: [],
      sortColumn: '',
      sortDirection: 'asc', // or 'desc'
    };
  },
  computed: {
    filteredUsers() {
      return this.users.filter(user => {
        const searchMatch = user.firstname.toLowerCase().includes(this.search.toLowerCase()) ||
        user.lastname.toLowerCase().includes(this.search.toLowerCase()) ||
        user.email.toLowerCase().includes(this.search.toLowerCase()) ||
        user.departments.toLowerCase().includes(this.search.toLowerCase());
        const departmentMatch = this.selectedDepartment === '' || user.departments.includes(this.selectedDepartment);
        return searchMatch && departmentMatch;
      });
    },
    paginatedUsers() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.filteredUsers.slice(start, end);
    },
    totalPages() {
      return Math.ceil(this.filteredUsers.length / this.itemsPerPage);
    },
    visiblePages() {
      let start = Math.max(1, this.currentPage - 2);
      let end = Math.min(this.totalPages, start + 4);
      start = Math.max(1, end - 4);
      return Array.from({length: end - start + 1}, (_, i) => start + i);
    },
    currentGroups() {
      return [...new Set(this.selectedUsers.flatMap(user => user.groups.split(';')))];
    },
  },
  methods: {
    uploadCSV(event) {
      const file = event.target.files[0];
      const formData = new FormData();
      formData.append('file', file);
      axios.post('/upload', formData)
      .then(response => {
        console.log(response.data.message);
        this.getUsers();
        this.getGroups();
      })
      .catch(error => {
        console.error(error);
      });
    },
    getUsers() {
      axios.get('/users', {
        params: {
          search: this.search,
          department: this.selectedDepartment,
        },
      })
      .then(response => {
        this.users = response.data;
        this.departments = [...new Set(this.users.flatMap(user => user.departments.split(',')))];
        this.resetPage();
      })
      .catch(error => {
        console.error(error);
      });
    },
    getGroups() {
      axios.get('/groups')
      .then(response => {
        this.availableGroups = response.data;
      })
      .catch(error => {
        console.error(error);
      });
    },
    filterUsers() {
      this.getUsers();
      this.clearSelections();
    },

    // existing methods
    sortUsers(column) {
      if (this.sortColumn === column) {
        // If the same column is clicked, toggle the direction
        this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortColumn = column;
        this.sortDirection = 'asc';
      }

      this.users.sort((a, b) => {
        if (a[column] < b[column]) return this.sortDirection === 'asc' ? -1 : 1;
        if (a[column] > b[column]) return this.sortDirection === 'asc' ? 1 : -1;
        return 0;
      });
    },

    changePage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page;
      }
    },
    resetPage() {
      this.currentPage = 1;
    },
    toggleSelectAll() {
      this.selectedUsers = this.selectAll ? [...this.filteredUsers] : [];
    },
    updateGroups() {
      const userIds = this.selectedUsers.map(user => `${user.firstname}_${user.lastname}_${user.email}`);
      axios.post('/update-groups', {
        userIds: userIds,
        groupsToAdd: this.groupsToAdd,
        groupsToRemove: this.groupsToRemove,
      })
      .then(response => {
        console.log(response.data.message);
        this.getUsers();
        this.showGroupModal = false;
        this.groupsToAdd = [];
        this.groupsToRemove = [];
      })
      .catch(error => {
        console.error(error);
      });
    },
    addNewGroup() {
      if (this.newGroup && !this.availableGroups.includes(this.newGroup)) {
        this.availableGroups.push(this.newGroup);
        this.groupsToAdd.push(this.newGroup);
        this.newGroup = '';
      }
    },
    exportCSV() {
      axios.get('/export', { responseType: 'blob' })
      .then(response => {
        const blob = new Blob([response.data], { type: 'text/csv' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'exported_users.csv';
        link.click();
      })
      .catch(error => {
        console.error(error);
      });
    },
    clearSelections() {
      this.selectedUsers = [];
      this.selectAll = false;
    },
  },
  watch: {
    search: debounce(function() {
      this.filterUsers();
    }, 300),
    selectedDepartment() {
      this.filterUsers();
    }
  },
  created() {
    this.getUsers();
    this.getGroups();
  },
};
</script>

<style>
#app {
  margin-top: 20px;
}
.modal {
  background-color: rgba(0, 0, 0, 0.5);
}
</style>
