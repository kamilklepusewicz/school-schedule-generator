<script setup>
import { computed, onMounted } from 'vue';
import AppPageHeader from '../components/AppPageHeader.vue';
import { useSchoolAdminData } from '../composables/useSchoolAdminData';

const { state, dashboardStats, ensureLoaded } = useSchoolAdminData();

onMounted(async () => {
  await ensureLoaded();
});

const recentTeachers = computed(() => state.teachers.slice(0, 5));
</script>

<template>
  <section class="layout">
    <AppPageHeader
      title="School Timetabling Control Center"
      description="Manage operational data, then request automatic timetable generation for all class groups."
    />

    <section class="stats-grid">
      <article v-for="item in dashboardStats" :key="item.key" class="card stat-card">
        <p class="muted">{{ item.label }}</p>
        <p class="stat-value">{{ item.value }}</p>
      </article>
    </section>

    <section class="workspace-grid">
      <article class="card quick-actions">
        <h2 class="section-title">Quick Actions</h2>
        <p class="muted">Jump directly to the three core administrator workflows.</p>

        <div class="quick-actions__buttons">
          <RouterLink to="/admin-data" class="btn btn-primary">Manage Master Data</RouterLink>
          <RouterLink to="/style-guide" class="btn">Open Style Guide</RouterLink>
        </div>
      </article>

      <article class="card">
        <h2 class="section-title">Recently Added Teachers</h2>
        <p v-if="!recentTeachers.length" class="muted">
          No teachers defined yet. Start in Data Management.
        </p>

        <div v-else class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>Name</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="entry in recentTeachers" :key="entry.id">
                <td>{{ entry.name }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>
    </section>
  </section>
</template>

<style scoped>
.layout {
  display: grid;
  gap: 1rem;
}

.stats-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(6, minmax(0, 1fr));
}

.stat-card {
  display: grid;
  gap: 0.35rem;
}

.stat-card .muted {
  margin: 0;
}

.stat-value {
  margin: 0;
  font-size: 1.65rem;
  font-weight: 700;
  color: var(--color-accent-strong);
}

.workspace-grid {
  display: grid;
  grid-template-columns: minmax(280px, 360px) 1fr;
  gap: 1rem;
}

.quick-actions {
  height: fit-content;
}

.quick-actions__buttons {
  display: grid;
  gap: 0.55rem;
  margin-top: 0.85rem;
}

@media (max-width: 900px) {
  .stats-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .workspace-grid,
  .quick-actions__buttons {
    grid-template-columns: 1fr;
  }
}
</style>
