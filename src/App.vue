<template>
  <div id="app" class="container mt-4">
    <h1 class="mb-4">User Group Management</h1>

    <div class="mb-3">
      <label for="csvFile" class="form-label">Upload CSV File</label>
      <input type="file" class="form-control" id="csvFile" @change="uploadCSV" accept=".csv">
    </div>

    <div class="row mb-3">
      <div class="col-md-6">
        <input v-model="search" class="form-control" placeholder="Search...">
      </div>
      <div class="col-md-6">
        <input v-model="departmentFilter" class="form-control" placeholder="Filter by department">
      </div>
    </div>

    <div class="table-responsive">
      <table class="table table-striped table-hover">
        <thead class="table-dark">
          <tr>
            <th><input type="checkbox" @change="selectAll" v-model="allSelected"></th>
            <th>First Name</th>
            <th>Last Name</th>
            <th>Email</th>
            <th>Departments</th>
            <th>Groups</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.email">
            <td>
              <input type="checkbox" v-model="selectedUsers" :value="user.firstname + '_' + user.lastname + '_' + user.email">
            </td>
            <td>{{ user.firstname }}</td>
            <td>{{ user.lastname }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.departments }}</td>
            <td>{{ user.groups }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="row mb-3">
      <div class="col-md-6">
        <div class="input-group">
          <input v-model="groupToAdd" class="form-control" placeholder="Add group">
          <button class="btn btn-primary" @click="addGroup">Add Group</button>
        </div>
      </div>
      <div class="col-md-6">
        <div class="input-group">
          <select v-model="groupToRemove" class="form-select">
            <option value="">Select group to remove</option>
            <option v-for="group in allGroups" :key="group" :value="group">{{ group }}</option>
          </select>
          <button class="btn btn-danger" @click="removeGroup">Remove Group</button>
        </div>
      </div>
    </div>

    <button class="btn btn-success" @click="exportCSV">Export CSV</button>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      users: [],
      search: '',
      departmentFilter: '',
      selectedUsers: [],
      groupToAdd: '',
      groupToRemove: '',
      allSelected: false,
    };
  },
  computed: {
    filteredUsers() {
      return this.users.filter(user => {
        const searchMatch = this.search === '' ||
          user.firstname.toLowerCase().includes(this.search.toLowerCase()) ||
          user.lastname.toLowerCase().includes(this.search.toLowerCase()) ||
          user.email.toLowerCase().includes(this.search.toLowerCase());

        const departmentMatch = this.departmentFilter === '' ||
          (user.departments && user.departments.includes(this.departmentFilter));

        return searchMatch && departmentMatch;
      });
    },
    allGroups() {
      const groups = new Set();
      this.users.forEach(user => {
        if (user.groups) {
          user.groups.split(';').forEach(group => groups.add(group));
        }
      });
      return Array.from(groups);
    },
  },
  methods: {
    async uploadCSV(event) {
      const file = event.target.files[0];
      const formData = new FormData();
      formData.append('file', file);
      await axios.post('http://localhost:5000/upload', formData);
      this.fetchUsers();
    },
    async fetchUsers() {
      const response = await axios.get(`http://localhost:5000/users?search=${this.search}&department=${this.departmentFilter}`);
      this.users = response.data;
    },
    async addGroup() {
      if (!this.groupToAdd) return;
      await axios.post('http://localhost:5000/update-groups', {
        userIds: this.selectedUsers,
        groupsToAdd: [this.groupToAdd],
        groupsToRemove: [],
      });
      this.groupToAdd = '';
      this.fetchUsers();
    },
    async removeGroup() {
      if (!this.groupToRemove) return;
      await axios.post('http://localhost:5000/update-groups', {
        userIds: this.selectedUsers,
        groupsToAdd: [],
        groupsToRemove: [this.groupToRemove],
      });
      this.groupToRemove = '';
      this.fetchUsers();
    },
    async exportCSV() {
      const response = await axios.get('http://localhost:5000/export', { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'exported_users.csv');
      document.body.appendChild(link);
      link.click();
    },
    selectAll() {
      if (this.allSelected) {
        this.selectedUsers = this.filteredUsers.map(user => `${user.firstname}_${user.lastname}_${user.email}`);
      } else {
        this.selectedUsers = [];
      }
    },
  },
  mounted() {
    this.fetchUsers();
  },
  watch: {
    search() {
      this.fetchUsers();
    },
    departmentFilter() {
      this.fetchUsers();
    },
  },
};
</script>
