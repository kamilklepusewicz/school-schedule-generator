<script setup>
import { computed, onMounted, ref, watch } from 'vue';
import AppPageHeader from '../components/AppPageHeader.vue';
import { useSchoolAdminData } from '../composables/useSchoolAdminData';

const { state, isLoading, ensureLoaded, fetchTimetableEntries } = useSchoolAdminData();

const selectedGroupId = ref('');
const feedback = ref('');
const weekDays = [
  { value: 1, label: 'Monday' },
  { value: 2, label: 'Tuesday' },
  { value: 3, label: 'Wednesday' },
  { value: 4, label: 'Thursday' },
  { value: 5, label: 'Friday' }
];

onMounted(async () => {
  await ensureLoaded();

  if (state.student_group.length) {
    selectedGroupId.value = state.student_group[0].id;
  }
});

watch(selectedGroupId, async (value) => {
  feedback.value = '';

  if (!value) {
    state.timetableEntries = [];
    return;
  }

  try {
    await fetchTimetableEntries(value);
  } catch (error) {
    feedback.value = error.message;
  }
});

const selectedGroup = computed(
  () => state.student_group.find((item) => item.id === selectedGroupId.value) || null
);

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

function roomName(roomId) {
  return state.classroom.find((item) => item.id === roomId)?.name || '-';
}

function lessonMeta(lesson) {
  return `${teacherName(lesson.teacher_id)} | ${roomName(lesson.classroom_id)}`;
}
</script>

<template>
  <section class="management-layout">
    <AppPageHeader
      title="Timetables Management"
      description="Pick a class group to inspect the real timetable stored in the backend lessons table."
    />

    <section class="management-grid">
      <article class="card selector-card">
        <h2 class="section-title">Choose Class Group</h2>
        <p class="muted">
          The app stores one timetable dataset in the backend. This view filters it by class group.
        </p>

        <label class="field">
          <span class="label-text">Class Group</span>
          <select v-model="selectedGroupId" class="control" :disabled="isLoading || !state.student_group.length">
            <option value="">Select a class group...</option>
            <option v-for="group in state.student_group" :key="group.id" :value="group.id">
              {{ group.name }}
            </option>
          </select>
        </label>

        <div class="group-summary" v-if="selectedGroup">
          <p><strong>Selected:</strong> {{ selectedGroup.name }}</p>
          <p><strong>Lessons:</strong> {{ selectedLessons.length }}</p>
        </div>

        <p v-else class="muted">Select a class group to render its timetable.</p>
      </article>

      <article class="card timetable-card">
        <h2 class="section-title">Timetable</h2>

        <p v-if="feedback" class="feedback">{{ feedback }}</p>
        <p v-else-if="!selectedGroup" class="muted">No class group selected.</p>
        <p v-else-if="!selectedLessons.length" class="muted">No lessons found for this class group.</p>
        <p v-else class="muted timetable-caption">
          Showing {{ selectedLessons.length }} lessons for {{ selectedGroup.name }}.
        </p>

        <div v-if="selectedGroup && selectedLessons.length" class="table-wrap">
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
