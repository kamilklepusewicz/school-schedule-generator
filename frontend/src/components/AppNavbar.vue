<template>
  <nav class="app-navbar">
    <div class="app-navbar__brand">
      <span class="app-navbar__logo" aria-hidden="true">SG</span>
      <div>
        <p class="app-navbar__title">Institution Timetabling</p>
        <p class="app-navbar__subtitle">Administrator workspace</p>
      </div>
    </div>

    <ul class="app-navbar__links" aria-label="Main navigation">
      <li><RouterLink to="/" class="app-link" active-class="is-active">Dashboard</RouterLink></li>
      <li>
        <RouterLink to="/admin-data" class="app-link" active-class="is-active">Data Management</RouterLink>
      </li>
      <li>
        <RouterLink to="/style-guide" class="app-link" active-class="is-active">Style Guide</RouterLink>
      </li>
    </ul>
  </nav>
</template>

<style scoped>
.app-navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.9rem 1.2rem;
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border-strong);
  background: var(--color-surface);
  box-shadow: var(--shadow-soft);
}

.app-navbar__brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.app-navbar__logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 50%;
  background: var(--color-accent-soft);
  color: var(--color-accent-strong);
  font-weight: 700;
  letter-spacing: 0.03em;
}

.app-navbar__title {
  margin: 0;
  font-weight: 600;
}

.app-navbar__subtitle {
  margin: 0;
  color: var(--color-text-muted);
  font-size: 0.84rem;
}

.app-navbar__links {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.app-link {
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--color-border);
  background: var(--color-surface-2);
  color: var(--color-text-main);
  padding: 0.45rem 0.75rem;
  border-radius: var(--radius-md);
  text-decoration: none;
  font: inherit;
}

.app-link.is-active {
  border-color: var(--color-accent);
  background: var(--color-accent-soft);
}

.app-link.is-disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

@media (max-width: 760px) {
  .app-navbar {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
