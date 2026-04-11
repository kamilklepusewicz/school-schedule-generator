<script setup>
import AppFooter from './components/AppFooter.vue';
import AppNavbar from './components/AppNavbar.vue';
</script>

<template>
  <div class="app-shell">
    <AppNavbar />

    <main class="app-main">
      <RouterView />
    </main>

    <AppFooter />
  </div>
</template>

<style scoped>
.app-shell {
  max-width: 1160px;
  margin: 0 auto;
  padding: 1.1rem;
  display: grid;
  gap: 1rem;
}

.app-main {
  min-height: 70vh;
}
</style>
