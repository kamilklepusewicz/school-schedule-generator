<script setup>
import { computed, onMounted, reactive, ref } from 'vue';
import AppPageHeader from '../components/AppPageHeader.vue';
import { useSchoolAdminData } from '../composables/useSchoolAdminData';

const { state, ensureLoaded, requestTimetableGeneration, lastGenerationRequest } = useSchoolAdminData();

const requestForm = reactive({
  target_group_id: ''
});

const requestStatus = ref('');

onMounted(async () => {
  await ensureLoaded();
});

const groupOptions = computed(() => state.student_group);

async function onGenerate() {
  requestStatus.value = '';

  try {
    await requestTimetableGeneration({
      target_group_id: requestForm.target_group_id || 'all'
    });
    requestStatus.value = 'Generation request queued successfully. The backend will process timetable creation based on lesson hours per subject per group.';
  } catch (error) {
    requestStatus.value = error.message;
  }
}
</script>

<template>
  <section class="generation-layout">
    <AppPageHeader
      title="Automatic Timetable Generation"
      description="Submit timetable generation requests for all groups or for a specific group and monitor request metadata."
    />

    <section class="generation-grid">
      <article class="card">
        <h2 class="section-title">Create Generation Request</h2>

        <form class="generation-form" @submit.prevent="onGenerate">
          <p class="form-info">
            Timetable generation will create a schedule based on the lesson hours configured for each subject per student group.
          </p>

          <label class="field full-width">
            <span class="label-text">Select Group (optional)</span>
            <select v-model="requestForm.target_group_id" class="control">
              <option value="">Generate for all groups</option>
              <option v-for="group in groupOptions" :key="group.id" :value="group.id">
                {{ group.name }}
              </option>
            </select>
          </label>

          <button type="submit" class="btn btn-primary">Generate Timetables</button>
        </form>
      </article>

      <article class="card">
        <h2 class="section-title">Request Status</h2>
        <p v-if="!requestStatus" class="muted">No generation request submitted yet.</p>
        <p v-else>{{ requestStatus }}</p>

        <div v-if="lastGenerationRequest" class="request-meta">
          <h3>Last Request Metadata</h3>
          <ul>
            <li><strong>Request ID:</strong> {{ lastGenerationRequest.request_id }}</li>
            <li><strong>Status:</strong> {{ lastGenerationRequest.status }}</li>
            <li><strong>Created At:</strong> {{ lastGenerationRequest.created_at }}</li>
            <li><strong>Scope:</strong> {{ lastGenerationRequest.target_group_name }}</li>
            <li><strong>Created Timetable Group:</strong> {{ lastGenerationRequest.generated_group_name }}</li>
          </ul>
        </div>
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

.full-width {
  grid-column: 1 / -1;
}

.request-meta {
  margin-top: 1rem;
  border-top: 1px solid var(--color-border);
  padding-top: 0.8rem;
}

.request-meta h3 {
  margin: 0 0 0.55rem;
  font-size: 1rem;
}

.request-meta ul {
  margin: 0;
  padding-left: 1.1rem;
}

@media (max-width: 900px) {
  .generation-grid,
  .generation-form {
    grid-template-columns: 1fr;
  }
}
</style>
