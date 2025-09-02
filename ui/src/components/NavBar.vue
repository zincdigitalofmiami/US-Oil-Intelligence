<template>
  <nav class="bg-gray-800 text-white p-4">
    <div class="container mx-auto flex justify-between">
      <router-link to="/" class="font-bold">Soy Intel</router-link>
      <div>
        <router-link to="/" class="mr-4">Home</router-link>
        <!-- Admin Dropdown -->
        <div class="relative inline-block text-left">
          <div>
            <button @click="adminOpen = !adminOpen" type="button" class="inline-flex justify-center w-full rounded-md border border-gray-700 shadow-sm px-4 py-2 bg-gray-800 text-sm font-medium text-white hover:bg-gray-700 focus:outline-none">
              Admin
              <!-- Heroicon: chevron-down -->
              <svg class="-mr-1 ml-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
          <div v-if="adminOpen" class="origin-top-right absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5">
            <div class="py-1" role="menu" aria-orientation="vertical" aria-labelledby="options-menu">
              <router-link to="/admin/secrets" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" role="menuitem">Secrets Management</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'NavBar',
  data() {
    return {
      adminOpen: false
    }
  }
}
</script>
