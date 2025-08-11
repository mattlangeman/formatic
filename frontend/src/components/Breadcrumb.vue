<template>
  <nav class="flex mb-6" aria-label="Breadcrumb">
    <ol class="inline-flex items-center space-x-1 md:space-x-3">
      <li 
        v-for="(item, index) in breadcrumbItems" 
        :key="index"
        class="inline-flex items-center"
      >
        <!-- First item (Home) with home icon -->
        <template v-if="index === 0">
          <router-link 
            :to="item.to" 
            class="inline-flex items-center text-sm font-medium text-gray-700 hover:text-primary-600"
          >
            <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
            </svg>
            {{ item.label }}
          </router-link>
        </template>
        
        <!-- Middle items with separator -->
        <template v-else-if="index < breadcrumbItems.length - 1">
          <div class="flex items-center">
            <svg class="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
            <router-link 
              :to="item.to" 
              class="ml-1 text-sm font-medium text-gray-700 hover:text-primary-600 md:ml-2"
            >
              {{ item.label }}
            </router-link>
          </div>
        </template>
        
        <!-- Last item (current page) - no link -->
        <template v-else>
          <div class="flex items-center" aria-current="page">
            <svg class="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
            <span class="ml-1 text-sm font-medium text-gray-500 md:ml-2">{{ item.label }}</span>
          </div>
        </template>
      </li>
    </ol>
  </nav>
</template>

<script>
export default {
  name: 'Breadcrumb',
  props: {
    items: {
      type: Array,
      required: true,
      // Expected format: [{ label: 'Home', to: '/' }, { label: 'Forms', to: '/forms' }]
    }
  },
  computed: {
    breadcrumbItems() {
      return this.items
    }
  }
}
</script>