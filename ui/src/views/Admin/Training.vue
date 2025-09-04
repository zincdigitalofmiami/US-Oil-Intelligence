<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">Model Training</h1>
    <div class="bg-white shadow-md rounded p-6">
      <p class="mb-4">
        Trigger the model retraining process by clicking the button below. This
        will start a background task on the server to retrain the forecasting
        model with the latest data.
      </p>
      <button
        @click="retrainModel"
        :disabled="isLoading"
        class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
      >
        <span v-if="isLoading">
          <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Training...
        </span>
        <span v-else>Retrain Model</span>
      </button>
      <div v-if="message" class="mt-4 p-4 rounded" :class="messageType === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'">
        {{ message }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      isLoading: false,
      message: "",
      messageType: "",
    };
  },
  methods: {
    async retrainModel() {
      this.isLoading = true;
      this.message = "";
      try {
        const response = await fetch("/api/admin/retrain-model", {
          method: "POST",
        });
        if (response.ok) {
          this.message = "Model training started successfully.";
          this.messageType = "success";
        } else {
          const errorData = await response.json();
          this.message = `Error: ${errorData.detail || 'Failed to start training.'}`;
          this.messageType = "error";
        }
      } catch (error) {
        this.message = `Error: ${error.message}`;
        this.messageType = "error";
      } finally {
        this.isLoading = false;
      }
    },
  },
};
</script>