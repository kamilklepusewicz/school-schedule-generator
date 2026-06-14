<script setup>
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import AppPageHeader from '../components/AppPageHeader.vue';
import { useSchoolAdminData } from '../composables/useSchoolAdminData';

const router = useRouter();
const { state, dashboardStats, ensureLoaded, isLoading, requestTimetableGeneration } = useSchoolAdminData();
const generationMessage = ref('');

const dashboardStatus = computed(() => {
  if (generationMessage.value) {
    return generationMessage.value;
  }

  return isLoading.value ? 'Generating timetable through the backend...' : '';
});

onMounted(async () => {
  await ensureLoaded();
});

const recentClasses = computed(() => state.classes.slice(0, 5));

function teacherName(id) {
  const teacher = state.teachers.find((item) => item.id === id);
  return teacher ? `${teacher.first_name} ${teacher.last_name}`.trim() : '-';
}

function subjectName(id) {
  return state.subjects.find((item) => item.id === id)?.name || '-';
}

function groupName(id) {
  return state.student_group.find((item) => item.id === id)?.name || '-';
}

function roomName(id) {
  const room = state.classroom.find((item) => item.id === id);
  return room ? room.name : '-';
}

async function generateTimetable() {
  generationMessage.value = '';

  try {
    await requestTimetableGeneration();
    generationMessage.value = 'Timetable generated successfully. Opening the management view.';
    await router.push('/timetable-management');
  } catch (error) {
    generationMessage.value = error.message;
  }
}
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
          <button type="button" class="btn btn-primary" :disabled="isLoading" @click="generateTimetable">
            Generate Timetable
          </button>
          <RouterLink to="/timetable-generation" class="btn">Timetable Generation</RouterLink>
          <RouterLink to="/timetable-management" class="btn">Manage Generated Timetables</RouterLink>
        </div>
        <p v-if="dashboardStatus" class="muted dashboard-status">{{ dashboardStatus }}</p>
      </article>

      <article class="card">
        <h2 class="section-title">Recently Added Classes</h2>
        <p v-if="!recentClasses.length" class="muted">No classes defined yet. Start in Data Management.</p>

        <div v-else class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>Subject</th>
                <th>Teacher</th>
                <th>Class Group</th>
                <th>Class Room</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="entry in recentClasses" :key="entry.id">
                <td>{{ subjectName(entry.subject_id) }}</td>
                <td>{{ teacherName(entry.teacher_id) }}</td>
                <td>{{ groupName(entry.group_id) }}</td>
                <td>{{ roomName(entry.classroom_id) }}</td>
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
  grid-template-columns: repeat(5, minmax(0, 1fr));
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
