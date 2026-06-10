<script setup>
import { computed, ref, watch } from 'vue';

const props = defineProps({
  studentGroups: {
    type: Array,
    required: true
  },
  subjects: {
    type: Array,
    required: true
  },
  lessonCounts: {
    type: Array,
    required: true
  },
  busy: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['save']);

const selectedGroupId = ref(null);
const hoursData = ref([]);

// Build lesson counts map for quick lookup
const lessonCountMap = computed(() => {
  const map = new Map();
  props.lessonCounts.forEach((lc) => {
    const key = `${lc.student_group_id}-${lc.subject_id}`;
    map.set(key, lc);
  });
  return map;
});

// Get lesson counts for selected group
const groupLessonCounts = computed(() => {
  if (!selectedGroupId.value) return [];
  
  return props.subjects.map((subject) => {
    const key = `${selectedGroupId.value}-${subject.id}`;
    const existing = lessonCountMap.value.get(key);
    return {
      student_group_id: selectedGroupId.value,
      subject_id: subject.id,
      subject_name: subject.name,
      id: existing?.id,
      hours: existing?.hours || 0
    };
  });
});

const selectedGroup = computed(() => {
  return props.studentGroups.find((g) => g.id === selectedGroupId.value);
});

watch(selectedGroupId, () => {
  hoursData.value = JSON.parse(JSON.stringify(groupLessonCounts.value));
});

function updateHours(subjectId, newHours) {
  const item = hoursData.value.find((h) => h.subject_id === subjectId);
  if (item) {
    item.hours = Math.max(0, newHours);
  }
}

function saveLessonCounts() {
  if (!selectedGroupId.value) {
    return;
  }
  
  emit('save', {
    studentGroupId: selectedGroupId.value,
    lessonCounts: hoursData.value.map((item) => ({
      id: item.id,
      student_group_id: item.student_group_id,
      subject_id: item.subject_id,
      hours: Number(item.hours)
    }))
  });
}

function resetData() {
  hoursData.value = JSON.parse(JSON.stringify(groupLessonCounts.value));
}
</script>

<template>
  <section class="lesson-count-panel">
    <article class="card">
      <div class="panel-header">
        <div>
          <h2 class="section-title">Lesson Hours</h2>
          <p class="muted">Set the number of hours for each subject per student group.</p>
        </div>
      </div>

      <div class="group-selector">
        <label class="field">
          <span class="label-text">Select Student Group</span>
          <select v-model.number="selectedGroupId" class="control">
            <option :value="null">Choose a student group...</option>
            <option v-for="group in studentGroups" :key="group.id" :value="group.id">
              {{ group.name }}
            </option>
          </select>
        </label>
      </div>

      <div v-if="selectedGroup" class="hours-editor">
        <p class="group-info">
          Editing hours for <strong>{{ selectedGroup.name }}</strong>
        </p>

        <div v-if="hoursData.length === 0" class="muted">
          No subjects available. Create subjects first.
        </div>

        <div v-else class="hours-list">
          <div v-for="item in hoursData" :key="item.subject_id" class="hours-item">
            <label class="subject-label">{{ item.subject_name }}</label>
            <input
              v-model.number="item.hours"
              type="number"
              class="control hours-input"
              min="0"
              :disabled="busy"
              @input="(e) => updateHours(item.subject_id, e.target.value)"
            />
            <span class="hours-unit">hours</span>
          </div>
        </div>

        <div class="actions">
          <button
            type="button"
            class="btn btn-primary"
            :disabled="busy || hoursData.length === 0"
            @click="saveLessonCounts"
          >
            Save All Hours
          </button>
          <button
            type="button"
            class="btn"
            :disabled="busy"
            @click="resetData"
          >
            Reset
          </button>
        </div>
      </div>
    </article>
  </section>
</template>

<style scoped>
.lesson-count-panel {
  display: grid;
  gap: 1rem;
}

.panel-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.6rem 1rem;
  align-items: flex-start;
  margin-bottom: 0.9rem;
}

.panel-header .muted {
  margin: 0;
}

.group-selector {
  margin-bottom: 1.5rem;
}

.group-selector .field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-width: 400px;
}

.group-info {
  padding: 0.75rem 1rem;
  background: var(--color-accent-soft);
  border-left: 4px solid var(--color-accent);
  border-radius: var(--radius-md);
  margin: 0 0 1rem 0;
  font-size: 0.95rem;
}

.hours-editor {
  margin-top: 1.5rem;
}

.hours-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: var(--color-surface-2);
  border-radius: var(--radius-md);
}

.hours-item {
  display: grid;
  grid-template-columns: 1fr auto 60px auto;
  gap: 0.75rem;
  align-items: center;
  padding: 0.75rem;
  background: var(--color-surface);
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
}

.subject-label {
  font-weight: 500;
  word-break: break-word;
}

.hours-input {
  width: 100%;
  text-align: center;
}

.hours-unit {
  color: var(--color-text-muted);
  font-size: 0.875rem;
}

.actions {
  display: flex;
  gap: 0.55rem;
  flex-wrap: wrap;
}

.btn {
  border: 1px solid var(--color-border);
  background: var(--color-surface-2);
  color: var(--color-text);
  padding: 0.5rem 1rem;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 0.95rem;
  transition: background 0.2s;
}

.btn:hover:not(:disabled) {
  background: var(--color-surface-3);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--color-accent);
  color: white;
  border-color: var(--color-accent);
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-accent-strong);
}

@media (max-width: 600px) {
  .hours-item {
    grid-template-columns: 1fr auto;
  }

  .hours-unit {
    grid-column: 2;
  }
}
</style>
