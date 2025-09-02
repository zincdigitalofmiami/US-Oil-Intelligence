<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">Secrets Management</h1>

    <!-- Form to Add a New Secret -->
    <div class="bg-white p-6 rounded-lg shadow-md mb-6">
      <h2 class="text-xl font-semibold mb-4">Add New Secret</h2>
      <div class="flex space-x-4">
        <input 
          v-model="newSecret.id" 
          placeholder="Secret Name (e.g., usda-api-key)"
          class="flex-grow p-2 border rounded"
        />
        <input 
          v-model="newSecret.value" 
          placeholder="Secret Value (the API Key)"
          type="password"
          class="flex-grow p-2 border rounded"
        />
        <button 
          @click="addSecret"
          class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Add Secret
        </button>
      </div>
       <p v-if="addMessage" class="text-green-500 mt-2">{{ addMessage }}</p>
    </div>

    <!-- List of Existing Secrets -->
    <div class="bg-white p-6 rounded-lg shadow-md">
      <h2 class="text-xl font-semibold mb-4">Existing Secrets</h2>
      <ul v-if="secrets.length > 0">
        <li 
          v-for="secret in secrets" 
          :key="secret"
          class="border-b py-2 flex justify-between items-center"
        >
          <span>{{ secret }}</span>
        </li>
      </ul>
      <p v-else class="text-gray-500">No secrets found.</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'SecretsManagement',
  data() {
    return {
      secrets: [],
      newSecret: {
        id: '',
        value: ''
      },
      addMessage: ''
    };
  },
  methods: {
    async fetchSecrets() {
      try {
        const response = await axios.get('/api/admin/secrets');
        this.secrets = response.data;
      } catch (error) {
        console.error("Error fetching secrets:", error);
      }
    },
    async addSecret() {
      if (!this.newSecret.id || !this.newSecret.value) {
        alert('Both secret name and value are required.');
        return;
      }
      try {
        await axios.post(`/api/admin/secrets/${this.newSecret.id}`, { 
          secret_value: this.newSecret.value 
        });
        this.addMessage = `Secret '${this.newSecret.id}' added successfully.`;
        this.newSecret.id = '';
        this.newSecret.value = '';
        await this.fetchSecrets(); // Refresh the list
      } catch (error) {
        console.error("Error adding secret:", error);
        this.addMessage = 'Failed to add secret.';
      }
    }
  },
  mounted() {
    this.fetchSecrets();
  }
};
</script>
