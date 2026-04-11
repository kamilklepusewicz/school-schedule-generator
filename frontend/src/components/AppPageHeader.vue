<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  }
});
</script>

<template>
  <header class="page-header card">
    <p class="eyebrow">Weekly Planner</p>
    <h1>{{ title }}</h1>
    <p class="description">{{ description }}</p>
  </header>
</template>

<style scoped>
.page-header h1 {
  margin: 0;
  font-size: clamp(1.5rem, 2vw, 2.1rem);
}

.eyebrow {
  margin: 0 0 0.35rem;
  color: var(--color-accent-strong);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 0.78rem;
  font-weight: 700;
}

.description {
  margin: 0.55rem 0 0;
  color: var(--color-text-muted);
  max-width: 62ch;
}
</style>
