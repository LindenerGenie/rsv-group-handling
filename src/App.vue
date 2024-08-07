<template>
  <div id="app" class="container">
    <h1>User Management</h1>
    <div class="mb-3">
      <input type="file" @change="uploadUserData" accept=".xlsx" />
    </div>
    <div id="searcharea">
      <div class="form-group">
        <input type="text" v-model="search" placeholder="Search by name, email, or department" class="form-control" />
      </div>
      <div class="form-group">
        <label>Sort Departments</label>
        <select v-model="selectedDepartment" class="form-control">
          <option value="">All Departments</option>
          <option v-for="department in sortedDepartments" :key="department" :value="department">{{ department }}</option>
        </select>
      </div>
      <div class="form-group">
        <label>Sort Available Groups</label>
        <select v-model="selectedGroup" class="form-control">
          <option value="">All Groups</option>
          <option v-for="group in sortedAvailableGroups" :key="group" :value="group">{{ group }}</option>
        </select>
      </div>
    </div>
    <div class="mb-3">
      <button @click="showGroupModal = true" class="btn btn-primary" :disabled="selectedUsers.length === 0">Manage Groups</button>
      <button @click="exportUserData" class="btn btn-success ml-2">Export UserData</button>
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
          <th @click="sortUsers('lastModified')">Last Modified (in App)</th>
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
          <td>{{ formatCreatedDate(user.lastModified) }}</td>
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
            <button type="button" class="close align-right" @click="showGroupModal = false">
              <span>&times;</span>
            </button>
          </div>
          <div class="modal-body">
            <p>Use this dialog to manage groups for selected users. You can add new groups, remove existing groups, and assign users to different groups.</p>
            <div class="form-group">
              <div class="d-flex">
                <div class="mr-2">
                  <label>Add Groups:</label>
                  <select v-model="groupsToAdd" multiple class="form-control">
                    <option v-for="group in groupsAvailableForAddition" :key="group" :value="group">{{ group }}</option>
                  </select>
                </div>
                <div class="ml-auto">
                  <label>New Group:</label>
                  <input v-model="newGroup" class="form-control" placeholder="Enter new group name" />
                  <button @click="addNewGroup" class="btn btn-secondary mt-2">Add New Group</button>
                </div>
              </div>
            </div>
            <div class="form-group">
              <label>Remove Groups:</label>
              <select v-model="groupsToRemove" multiple class="form-control">
                <option v-for="group in groupsAvailableForRemoval" :key="group" :value="group">{{ group }}</option>
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
      users: [], // Initialize as an empty array
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
      selectedGroup: '',
    };
  },
  async getUsers() {
    try {
      const response = await axios.get('/users', {
        params: {
          search: this.search,
          department: this.selectedDepartment,
        },
      });
      this.users = Array.isArray(response.data) ? response.data : [];
      this.departments = [...new Set(this.users.flatMap(user => user.departments.split(',')))];
      this.resetPage();
    } catch (error) {
      console.error(error);
    }
  },
  computed: {
    filteredUsers() {
      return this.users.filter(user => {
        const searchMatch = user.firstname.toLowerCase().includes(this.search.toLowerCase()) ||
        user.lastname.toLowerCase().includes(this.search.toLowerCase()) ||
        user.email.toLowerCase().includes(this.search.toLowerCase()) ||
        user.departments.toLowerCase().includes(this.search.toLowerCase());
        const departmentMatch = this.selectedDepartment === '' || user.departments.includes(this.selectedDepartment);
        const groupMatch = this.selectedGroup === '' || user.groups.split(';').includes(this.selectedGroup);
        return searchMatch && departmentMatch && groupMatch;
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
    sortedDepartments() {
      return this.departments.sort();
    },
    sortedAvailableGroups() {
      return this.availableGroups.sort();
    },
    groupsAvailableForRemoval() {
      const selectedGroups = this.selectedUsers.flatMap(user => user.groups.split(';'));
      return [...new Set(selectedGroups)].filter(group => this.currentGroups.includes(group));
    },
    groupsAvailableForAddition() {
      const selectedGroups = this.selectedUsers.flatMap(user => user.groups.split(';'));
      const allGroups = this.availableGroups;
      const unselectedGroups = allGroups.filter(group => !selectedGroups.includes(group));
      console.log('Selected Groups:', selectedGroups);
      console.log('All Groups:', allGroups);
      console.log('Unselected Groups:', unselectedGroups);
      return unselectedGroups;
    },
    sortedCurrentGroups() {
      // Assuming `currentGroups` is a data property that holds the groups a user currently has.
      // This will also need to be computed dynamically similar to `availableGroups`.
      return this.currentGroups.sort();
    },
    visiblePages() {
      let start = Math.max(1, this.currentPage - 2);
      let end = Math.min(this.totalPages, start + 4);
      start = Math.max(1, end - 4);
      return Array.from({ length: end - start + 1 }, (_, i) => start + i);
    },
    currentGroups() {
      return [...new Set(this.selectedUsers.flatMap(user => user.groups.split(';')))];
    },
  },
  methods: {
    async uploadUserData(event) {
      const file = event.target.files[0];
      const formData = new FormData();
      formData.append('file', file);
      try {
        const response = await axios.post('/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        console.log('Upload successful', response.data);
        this.getUsers(); // Refresh users data after successful upload
        this.getGroups(); // Refresh groups data after successful upload
      } catch (error) {
        console.error('Upload failed', error.response ? error.response.data : error);
      }
    },
    exportUserData() {
      axios
      .get('/export', { responseType: 'arraybuffer' })
      .then(response => {
        const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'exported_users.xlsx';
        link.click();
      })
      .catch(error => {
        console.error(error);
      });
    },
    getUsers() {
      axios
      .get('/users', {
        params: {
          search: this.search,
          department: this.selectedDepartment,
        },
      })
      .then(response => {
        this.users = Array.isArray(response.data) ? response.data : [];
        this.departments = [...new Set(this.users.flatMap(user => user.departments.split(',')))];
        this.resetPage();
      })
      .catch(error => {
        console.error(error);
      });
    },
    getGroups() {
      // Example API call
      axios.get('/groups')
      .then(response => {
        this.availableGroups = Array.isArray(response.data) ? response.data : [];
      })
      .catch(error => {
        console.error(error);
        this.availableGroups = []; // Ensure it's reset to an array on error
      });
    },
    filterUsers() {
      this.getUsers();
      this.getGroups();
      this.clearSelections();
    },

    // Method to format the 'created' date
    // Method to format the 'created' or 'lastModified' date
    formatCreatedDate(dateString) {
      if (!dateString) return ''; // Return empty if dateString is empty
      // Check if dateString is in ISO 8601 format
      if (dateString.includes('T')) {
        const date = new Date(dateString);
        return date.toLocaleDateString('de-DE'); // Converts to 'dd.mm.yyyy'. Change 'de-DE' as needed
      }
      // Assuming the original format is 'dd.mm.yyyy'
      const [day, month, year] = dateString.split('.');
      return `${day}.${month}.${year}`; // Convert to 'dd.mm.yyyy'
    },

    // Modify the sortUsers method to handle date sorting
    sortUsers(column) {
      console.log('Sorting by:', column);
      if (this.sortColumn === column) {
        this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortColumn = column;
        this.sortDirection = 'asc';
      }
      if (column === 'lastModified') {
        this.users.sort((a, b) => {
          // Parse the dates from 'dd.mm.yyyy' to 'yyyy-mm-dd' for correct comparison
          const dateA = a.lastModified ? new Date(a.lastModified.split('.').reverse().join('-')) : new Date(0);
          const dateB = b.lastModified ? new Date(b.lastModified.split('.').reverse().join('-')) : new Date(0);
          return this.sortDirection === 'asc' ? dateA - dateB : dateB - dateA;
        });
      } else {
        this.users.sort((a, b) => {
          const valueA = a[column].toLowerCase();
          const valueB = b[column].toLowerCase();
          return this.sortDirection === 'asc' ? valueA.localeCompare(valueB) : valueB.localeCompare(valueA);
        });
      }
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
      axios
      .post('/update-groups', {
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
    clearSelections() {
      this.selectedUsers = [];
      this.selectAll = false;
    },
    watch: {
      search: debounce(function () {
        this.filterUsers();
      }, 300),
      selectedDepartment() {
        this.filterUsers();
      },
    },
    created() {
      this.getUsers();
      this.getGroups();
    },
  },
};

</script>

<style>
#app {
  margin-top: 20px;
}
#searcharea {
  display: flex;
  justify-content: space-between;
  padding-bottom: 1em;
}
.modal {
  background-color: rgba(0, 0, 0, 0.5);
}
thead th {
  cursor: pointer;
}
.align-right
{
  text-align: right;
}
</style>
