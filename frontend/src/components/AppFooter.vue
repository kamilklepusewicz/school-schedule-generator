<template>
  <footer class="app-footer card">
    <p class="app-footer__text">School Schedule Generator</p>
    <p class="app-footer__meta">Template-ready layout for forms, tables, and planning modules.</p>
  </footer>
</template>

<style scoped>
.app-footer {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.5rem 1rem;
}

.app-footer__text,
.app-footer__meta {
  margin: 0;
}

.app-footer__meta {
  color: var(--color-text-muted);
}
</style>
