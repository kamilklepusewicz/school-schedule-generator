<script setup>
import { computed, onMounted, ref } from 'vue';
import AppPageHeader from '../components/AppPageHeader.vue';
import { useSchoolAdminData } from '../composables/useSchoolAdminData';

const { ensureLoaded, requestTimetableGeneration, lastGenerationRequest, isLoading } = useSchoolAdminData();
const requestStatus = ref('');

onMounted(async () => {
  await ensureLoaded();
});

const generationMessage = computed(() => lastGenerationRequest.value?.message || '');

async function onGenerate() {
  requestStatus.value = '';

  try {
    await requestTimetableGeneration();
    requestStatus.value = 'Timetable generated successfully.';
  } catch (error) {
    requestStatus.value = error.message;
  }
}
</script>

<template>
  <section class="generation-layout">
    <AppPageHeader
      title="Automatic Timetable Generation"
      description="Generate the timetable directly through the backend scheduler."
    />

    <section class="generation-grid">
      <article class="card">
        <h2 class="section-title">Create Timetable</h2>

        <form class="generation-form" @submit.prevent="onGenerate">
          <p class="form-info">
            The backend will calculate the timetable from the current teachers, groups, classrooms, and lesson counts.
          </p>

          <button type="submit" class="btn btn-primary" :disabled="isLoading">
            Generate Timetable
          </button>
        </form>
      </article>

      <article class="card">
        <h2 class="section-title">Generation Status</h2>
        <p v-if="!requestStatus && !generationMessage" class="muted">No generation request submitted yet.</p>
        <p v-else>{{ requestStatus || generationMessage }}</p>
      </article>
    </section>
  </section>
</template>

<style scoped>
.generation-layout {
  display: grid;
  gap: 1rem;
}

.generation-grid {
  display: grid;
  grid-template-columns: minmax(300px, 1fr) minmax(300px, 1fr);
  gap: 1rem;
}

.generation-form {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
}

.form-info {
  margin: 0 0 0.5rem 0;
  padding: 0.75rem;
  background: var(--color-accent-soft);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  color: var(--color-text);
}

@media (max-width: 900px) {
  .generation-grid,
  .generation-form {
    grid-template-columns: 1fr;
  }
}
</style>
