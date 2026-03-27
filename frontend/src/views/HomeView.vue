<script setup>
import { computed, onMounted } from 'vue';
import AppPageHeader from '../components/AppPageHeader.vue';
import { useSchoolAdminData } from '../composables/useSchoolAdminData';

const { state, ensureLoaded } = useSchoolAdminData();

onMounted(async () => {
  await ensureLoaded();
});

const recentTeachers = computed(() => state.teachers.slice(0, 5));
const teachersCount = computed(() => state.teachers.length);

function teacherFullName(entry) {
  return `${entry.firstName} ${entry.lastName}`.trim();
}
</script>

<template>
  <section class="layout">
    <AppPageHeader
      title="School Timetabling Control Center"
      description="Manage operational data, then request automatic timetable generation for all class groups."
    />

    <section class="workspace-grid">
      <article class="card teacher-count-tile">
        <p class="muted">Teachers</p>
        <p class="teacher-count-tile__value">{{ teachersCount }}</p>
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
                <td>{{ teacherFullName(entry) }}</td>
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

.teacher-count-tile__value {
  margin: 0;
  font-size: 2.2rem;
  font-weight: 700;
  color: var(--color-accent-strong);
}

.workspace-grid {
  display: grid;
  grid-template-columns: minmax(280px, 360px) 1fr;
  gap: 1rem;
}

.teacher-count-tile {
  height: fit-content;
}

@media (max-width: 900px) {
  .workspace-grid {
    grid-template-columns: 1fr;
  }
}
</style>
