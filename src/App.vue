<template>
  <div id="app">
    <input type="file" @change="uploadCSV" accept=".csv">

    <div>
      <input v-model="search" placeholder="Search...">
      <input v-model="departmentFilter" placeholder="Filter by department">
    </div>

    <table>
      <thead>
        <tr>
          <th>Select</th>
          <th>First Name</th>
          <th>Last Name</th>
          <th>Email</th>
          <th>Departments</th>
          <th>Groups</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in filteredUsers" :key="user.email">
          <td><input type="checkbox" v-model="selectedUsers" :value="user.firstname + '_' + user.lastname + '_' + user.email"></td>
          <td>{{ user.firstname }}</td>
          <td>{{ user.lastname }}</td>
          <td>{{ user.email }}</td>
          <td>{{ user.departments }}</td>
          <td>{{ user.groups }}</td>
        </tr>
      </tbody>
    </table>

    <div>
      <input v-model="groupToAdd" placeholder="Add group">
      <button @click="addGroup">Add Group</button>
    </div>

    <div>
      <select v-model="groupToRemove">
        <option v-for="group in allGroups" :key="group" :value="group">{{ group }}</option>
      </select>
      <button @click="removeGroup">Remove Group</button>
    </div>

    <button @click="exportCSV">Export CSV</button>
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
      await axios.post('http://localhost:5000/update-groups', {
        userIds: this.selectedUsers,
        groupsToAdd: [this.groupToAdd],
        groupsToRemove: [],
      });
      this.groupToAdd = '';
      this.fetchUsers();
    },
    async removeGroup() {
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
  },
  mounted() {
    this.fetchUsers();
  },
};
</script>
