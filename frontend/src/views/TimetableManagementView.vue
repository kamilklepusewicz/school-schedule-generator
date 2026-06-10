<script setup>
import { computed, onMounted, ref, watch } from 'vue';
import AppPageHeader from '../components/AppPageHeader.vue';
import { useSchoolAdminData } from '../composables/useSchoolAdminData';

const { state, isLoading, ensureLoaded, fetchTimetableEntries } = useSchoolAdminData();

const selectedPerspective = ref('groups');
const selectedScopeId = ref('');
const feedback = ref('');
const weekDays = [
  { value: 1, label: 'Monday' },
  { value: 2, label: 'Tuesday' },
  { value: 3, label: 'Wednesday' },
  { value: 4, label: 'Thursday' },
  { value: 5, label: 'Friday' }
];

const perspectiveOptions = [
  { value: 'groups', label: 'Class Groups' },
  { value: 'teachers', label: 'Teachers' },
  { value: 'classrooms', label: 'Classrooms' }
];

onMounted(async () => {
  await ensureLoaded();
  syncSelectedScope();
});

watch(selectedPerspective, () => {
  state.timetableEntries = [];
  selectedScopeId.value = '';
  syncSelectedScope();
});

watch([selectedPerspective, selectedScopeId], async ([perspective, value]) => {
  feedback.value = '';

  if (!value) {
    state.timetableEntries = [];
    return;
  }

  try {
    await fetchTimetableEntries(perspective, value);
  } catch (error) {
    feedback.value = error.message;
  }
});

const scopeOptions = computed(() => {
  if (selectedPerspective.value === 'teachers') {
    return state.teachers.map((teacher) => ({
      id: teacher.id,
      label: `${teacher.first_name} ${teacher.last_name}`.trim()
    }));
  }

  if (selectedPerspective.value === 'classrooms') {
    return state.classroom.map((room) => ({
      id: room.id,
      label: room.name
    }));
  }

  return state.student_group.map((group) => ({
    id: group.id,
    label: group.name
  }));
});

const selectedScope = computed(() => {
  if (selectedPerspective.value === 'teachers') {
    return state.teachers.find((teacher) => teacher.id === selectedScopeId.value) || null;
  }

  if (selectedPerspective.value === 'classrooms') {
    return state.classroom.find((room) => room.id === selectedScopeId.value) || null;
  }

  return state.student_group.find((group) => group.id === selectedScopeId.value) || null;
});

const selectedLessons = computed(() =>
  [...state.timetableEntries].sort((left, right) => {
    if (left.day !== right.day) {
      return left.day - right.day;
    }

    return left.slot - right.slot;
  })
);

const maxSlot = computed(() => Math.max(8, ...selectedLessons.value.map((entry) => entry.slot)));

const gridRows = computed(() => {
  const rows = [];

  for (let slot = 1; slot <= maxSlot.value; slot += 1) {
    rows.push({
      slot,
      cells: weekDays.map((day) =>
        selectedLessons.value.filter((entry) => entry.day === day.value && entry.slot === slot)
      )
    });
  }

  return rows;
});

function syncSelectedScope() {
  const nextScopeId = scopeOptions.value[0]?.id || '';

  if (!selectedScopeId.value || !scopeOptions.value.some((item) => item.id === selectedScopeId.value)) {
    selectedScopeId.value = nextScopeId;
  }
}

function dayName(dayValue) {
  return weekDays.find((day) => day.value === dayValue)?.label || `Day ${dayValue}`;
}

function subjectName(subjectId) {
  return state.subjects.find((item) => item.id === subjectId)?.name || '-';
}

function teacherName(teacherId) {
  const teacher = state.teachers.find((item) => item.id === teacherId);
  return teacher ? `${teacher.first_name} ${teacher.last_name}`.trim() : '-';
}

function groupName(groupId) {
  return state.student_group.find((item) => item.id === groupId)?.name || '-';
}

function roomName(roomId) {
  return state.classroom.find((item) => item.id === roomId)?.name || '-';
}

function lessonMeta(lesson) {
  if (selectedPerspective.value === 'teachers') {
    return `${groupName(lesson.group_id)} | ${roomName(lesson.classroom_id)}`;
  }

  if (selectedPerspective.value === 'classrooms') {
    return `${groupName(lesson.group_id)} | ${teacherName(lesson.teacher_id)}`;
  }

  return `${teacherName(lesson.teacher_id)} | ${roomName(lesson.classroom_id)}`;
}

function scopeLabel() {
  return selectedScope.value?.label || selectedScope.value?.name || 'current selection';
}
</script>

<template>
  <section class="management-layout">
    <AppPageHeader
      title="Timetables Management"
      description="View the real timetable for one class group, teacher, or classroom at a time."
    />

    <section class="management-grid">
      <article class="card selector-card">
        <h2 class="section-title">Choose View</h2>
        <p class="muted">Only one timetable perspective can be active at a time.</p>

        <div class="perspective-switcher" role="tablist" aria-label="Timetable perspective">
          <button
            v-for="option in perspectiveOptions"
            :key="option.value"
            type="button"
            class="btn tab-btn"
            :class="{ 'is-active': selectedPerspective === option.value }"
            @click="selectedPerspective = option.value"
          >
            {{ option.label }}
          </button>
        </div>

        <label class="field">
          <span class="label-text">{{ perspectiveOptions.find((item) => item.value === selectedPerspective)?.label }}</span>
          <select v-model="selectedScopeId" class="control" :disabled="isLoading || !scopeOptions.length">
            <option value="">Select an item...</option>
            <option v-for="option in scopeOptions" :key="option.id" :value="option.id">
              {{ option.label }}
            </option>
          </select>
        </label>

        <div class="group-summary" v-if="selectedScope">
          <p><strong>Selected:</strong> {{ selectedScope.label || selectedScope.name || 'Current selection' }}</p>
          <p><strong>Lessons:</strong> {{ selectedLessons.length }}</p>
        </div>

        <p v-else class="muted">Select a {{ selectedPerspective === 'groups' ? 'class group' : selectedPerspective === 'teachers' ? 'teacher' : 'classroom' }} to render its timetable.</p>
      </article>

      <article class="card timetable-card">
        <h2 class="section-title">Timetable</h2>

        <p v-if="feedback" class="feedback">{{ feedback }}</p>
        <p v-else-if="!selectedScope" class="muted">No selection made yet.</p>
        <p v-else-if="!selectedLessons.length" class="muted">No lessons found for the selected timetable.</p>
        <p v-else class="muted timetable-caption">
          Showing {{ selectedLessons.length }} lessons for {{ scopeLabel() }}.
        </p>

        <div v-if="selectedScope && selectedLessons.length" class="table-wrap">
          <table class="table timetable-board">
            <thead>
              <tr>
                <th class="hour-col">Slot</th>
                <th v-for="day in weekDays" :key="day.value">{{ day.label }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in gridRows" :key="row.slot">
                <td class="hour-col">{{ row.slot }}</td>
                <td v-for="(cellEntries, index) in row.cells" :key="`${row.slot}-${weekDays[index].value}`">
                  <div v-if="cellEntries.length" class="lesson-stack">
                    <article v-for="lesson in cellEntries" :key="lesson.id" class="lesson-tile">
                      <p class="lesson-title">{{ subjectName(lesson.subject_id) }}</p>
                      <p class="lesson-meta">{{ lessonMeta(lesson) }}</p>
                      <p class="lesson-day">{{ dayName(lesson.day) }}</p>
                    </article>
                  </div>
                  <span v-else class="empty-slot">-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>
    </section>
  </section>
</template>

<style scoped>
.management-layout {
  display: grid;
  gap: 1rem;
}

.management-grid {
  display: grid;
  grid-template-columns: minmax(280px, 360px) 1fr;
  gap: 1rem;
}

.selector-card,
.timetable-card {
  height: fit-content;
}

.perspective-switcher {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.9rem;
}

.group-summary {
  margin-top: 0.85rem;
  padding: 0.75rem;
  border-radius: var(--radius-md);
  background: var(--color-accent-soft);
  display: grid;
  gap: 0.25rem;
}

.group-summary p,
.feedback,
.timetable-caption {
  margin: 0;
}

.feedback {
  margin-bottom: 0.75rem;
  color: var(--color-accent-strong);
}

.timetable-board .hour-col {
  width: 70px;
  min-width: 70px;
  text-align: center;
  font-weight: 700;
}

.lesson-stack {
  display: grid;
  gap: 0.4rem;
}

.lesson-tile {
  padding: 0.6rem;
  border-radius: var(--radius-md);
  background: var(--color-accent-soft);
  border: 1px solid var(--color-border);
}

.lesson-title,
.lesson-meta,
.lesson-day {
  margin: 0;
}

.lesson-title {
  font-weight: 700;
}

.lesson-meta,
.lesson-day {
  font-size: 0.84rem;
  color: var(--color-text-muted);
}

.empty-slot {
  color: var(--color-text-muted);
}

@media (max-width: 900px) {
  .management-grid {
    grid-template-columns: 1fr;
  }
}
</style>
