<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue';
import AppPageHeader from '../components/AppPageHeader.vue';
import { useSchoolAdminData } from '../composables/useSchoolAdminData';

const {
  state,
  isLoading,
  ensureLoaded,
  fetchTimetableEntries,
  moveTimetableEntry,
  swapTimetableEntriesById
} = useSchoolAdminData();

const selectedGroupId = ref('');
const perspective = ref('groups');
const selectedScope = ref('');
const feedback = ref('');
const weekDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];

const moveForm = reactive({
  entryId: '',
  day: 'Monday',
  slot: 1
});

const swapForm = reactive({
  firstId: '',
  secondId: ''
});

onMounted(async () => {
  await ensureLoaded();

  if (state.timetableGroups.length) {
    selectedGroupId.value = state.timetableGroups[0].id;
  }
});

watch(selectedGroupId, async (value) => {
  if (!value) {
    return;
  }

  await fetchTimetableEntries(value);
  selectedScope.value = '';
  moveForm.entryId = '';
  swapForm.firstId = '';
  swapForm.secondId = '';
});

watch(perspective, () => {
  selectedScope.value = '';
});

const selectedGroup = computed(
  () => state.timetableGroups.find((item) => item.id === selectedGroupId.value) || null
);

const perspectiveKeyMap = computed(() => ({
  groups: 'group_name',
  rooms: 'room_name',
  teachers: 'teacher_name'
}));

const currentPerspectiveKey = computed(
  () => perspectiveKeyMap.value[perspective.value] || 'group_name'
);

const scopeOptions = computed(() => {
  const unique = new Map();
  state.timetableEntries.forEach((entry) => {
    unique.set(entry[currentPerspectiveKey.value], entry[currentPerspectiveKey.value]);
  });
  return Array.from(unique.values());
});

const visibleEntries = computed(() => {
  if (!selectedScope.value) {
    return state.timetableEntries;
  }
  return state.timetableEntries.filter(
    (entry) => entry[currentPerspectiveKey.value] === selectedScope.value
  );
});

const entryOptions = computed(() =>
  state.timetableEntries.map((entry) => ({
    value: entry.id,
    label: `${entry.subject_name} | ${entry.group_name} | ${entry.day} ${entry.slot}`
  }))
);

const entriesByScope = computed(() => {
  const map = new Map();
  visibleEntries.value.forEach((entry) => {
    const scopeName = entry[currentPerspectiveKey.value];
    if (!map.has(scopeName)) {
      map.set(scopeName, []);
    }
    map.get(scopeName).push(entry);
  });
  return Array.from(map.entries()).map(([scope, entries]) => ({ scope, entries }));
});

function buildGridRows(entries) {
  const maxSlot = Math.max(8, ...entries.map((entry) => entry.slot));
  const rows = [];

  for (let slot = 1; slot <= maxSlot; slot += 1) {
    const dayCells = weekDays.map((day) =>
      entries.filter((entry) => entry.day === day && entry.slot === slot)
    );

    rows.push({
      slot,
      dayCells
    });
  }

  return rows;
}

function tileMeta(entry) {
  if (perspective.value === 'groups') {
    return `${entry.teacher_name} | ${entry.room_name}`;
  }

  if (perspective.value === 'rooms') {
    return `${entry.group_name} | ${entry.teacher_name}`;
  }

  return `${entry.group_name} | ${entry.room_name}`;
}

async function submitMove() {
  feedback.value = '';

  if (!selectedGroupId.value || !moveForm.entryId) {
    return;
  }

  try {
    await moveTimetableEntry(selectedGroupId.value, moveForm.entryId, {
      day: moveForm.day,
      slot: Number(moveForm.slot)
    });
    feedback.value = 'Class placement updated successfully.';
  } catch (error) {
    feedback.value = error.message;
  }
}

async function submitSwap() {
  feedback.value = '';

  if (!selectedGroupId.value || !swapForm.firstId || !swapForm.secondId) {
    return;
  }

  try {
    await swapTimetableEntriesById(selectedGroupId.value, swapForm.firstId, swapForm.secondId);
    feedback.value = 'Classes swapped successfully.';
  } catch (error) {
    feedback.value = error.message;
  }
}
</script>

<template>
  <section class="management-layout">
    <AppPageHeader
      title="Timetables Management"
      description="Open generated timetable groups and manually move or swap classes when fine-tuning schedules."
    />

    <section class="management-grid">
      <article class="card groups-list">
        <h2 class="section-title">Generated Timetable Groups</h2>

        <p v-if="!state.timetableGroups.length" class="muted">
          No generated groups yet. Use Timetable Generation first.
        </p>

        <div v-else class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Scope</th>
                <th>Status</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="group in state.timetableGroups"
                :key="group.id"
                :class="{ 'is-selected': selectedGroupId === group.id }"
                @click="selectedGroupId = group.id"
              >
                <td>{{ group.name }}</td>
                <td>{{ group.scope }}</td>
                <td>{{ group.status }}</td>
                <td>{{ new Date(group.created_at).toLocaleString() }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>

      <section class="details-grid">
        <article class="card">
          <h2 class="section-title">View Timetable Perspective</h2>

          <div class="controls-grid">
            <label class="field">
              <span class="label-text">Perspective</span>
              <select v-model="perspective" class="control" :disabled="!selectedGroup">
                <option value="groups">Class Groups</option>
                <option value="rooms">Class Rooms</option>
                <option value="teachers">Teachers</option>
              </select>
            </label>

            <label class="field">
              <span class="label-text">Filter</span>
              <select v-model="selectedScope" class="control" :disabled="!selectedGroup">
                <option value="">All</option>
                <option v-for="option in scopeOptions" :key="option" :value="option">{{ option }}</option>
              </select>
            </label>
          </div>
        </article>

        <article class="card">
          <h2 class="section-title">Manual Edits</h2>

          <div class="edit-grid">
            <form class="card nested-card" @submit.prevent="submitMove">
              <h3>Move Class</h3>
              <label class="field">
                <span class="label-text">Class</span>
                <select v-model="moveForm.entryId" class="control" :disabled="!selectedGroup">
                  <option value="">Select class...</option>
                  <option v-for="entry in entryOptions" :key="entry.value" :value="entry.value">
                    {{ entry.label }}
                  </option>
                </select>
              </label>
              <div class="pair-grid">
                <label class="field">
                  <span class="label-text">Day</span>
                  <select v-model="moveForm.day" class="control">
                    <option>Monday</option>
                    <option>Tuesday</option>
                    <option>Wednesday</option>
                    <option>Thursday</option>
                    <option>Friday</option>
                  </select>
                </label>
                <label class="field">
                  <span class="label-text">Hour Slot</span>
                  <input v-model.number="moveForm.slot" type="number" class="control" min="1" max="12" />
                </label>
              </div>
              <button type="submit" class="btn btn-primary" :disabled="isLoading">Apply Move</button>
            </form>

            <form class="card nested-card" @submit.prevent="submitSwap">
              <h3>Swap Two Classes</h3>
              <label class="field">
                <span class="label-text">Class A</span>
                <select v-model="swapForm.firstId" class="control" :disabled="!selectedGroup">
                  <option value="">Select class...</option>
                  <option v-for="entry in entryOptions" :key="entry.value" :value="entry.value">
                    {{ entry.label }}
                  </option>
                </select>
              </label>
              <label class="field">
                <span class="label-text">Class B</span>
                <select v-model="swapForm.secondId" class="control" :disabled="!selectedGroup">
                  <option value="">Select class...</option>
                  <option v-for="entry in entryOptions" :key="entry.value" :value="entry.value">
                    {{ entry.label }}
                  </option>
                </select>
              </label>
              <button type="submit" class="btn" :disabled="isLoading">Swap Slots</button>
            </form>
          </div>

          <p v-if="feedback" class="feedback">{{ feedback }}</p>
        </article>

        <article class="card">
          <h2 class="section-title">Timetable Details</h2>
          <p v-if="!selectedGroup" class="muted">Select a timetable group first.</p>
          <p v-else class="muted">
            Showing {{ visibleEntries.length }} classes from {{ selectedGroup.name }}.
          </p>

          <p v-if="selectedGroup && !entriesByScope.length" class="muted no-entries">
            No classes available for the selected perspective/filter.
          </p>

          <div v-for="scopeBlock in entriesByScope" :key="scopeBlock.scope" class="scope-board">
            <h3 class="scope-title">{{ scopeBlock.scope }}</h3>

            <div class="table-wrap">
              <table class="table timetable-board">
                <thead>
                  <tr>
                    <th class="hour-col">Hour</th>
                    <th v-for="day in weekDays" :key="day">{{ day }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in buildGridRows(scopeBlock.entries)" :key="row.slot">
                    <td class="hour-col">{{ row.slot }}</td>
                    <td v-for="(cellEntries, index) in row.dayCells" :key="`${row.slot}-${weekDays[index]}`">
                      <div v-if="cellEntries.length" class="lesson-stack">
                        <article
                          v-for="entry in cellEntries"
                          :key="entry.id"
                          class="lesson-tile"
                        >
                          <p class="lesson-title">{{ entry.subject_name }}</p>
                          <p class="lesson-meta">{{ tileMeta(entry) }}</p>
                        </article>
                      </div>
                      <span v-else class="empty-slot">-</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </article>
      </section>
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
  grid-template-columns: minmax(340px, 430px) 1fr;
  gap: 1rem;
}

.groups-list tbody tr {
  cursor: pointer;
}

.groups-list tbody tr.is-selected {
  background: var(--color-accent-soft);
}

.details-grid {
  display: grid;
  gap: 1rem;
}

.controls-grid,
.pair-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.edit-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.nested-card {
  box-shadow: none;
  border-style: dashed;
}

.nested-card h3 {
  margin: 0 0 0.6rem;
  font-size: 1rem;
}

.nested-card .btn {
  margin-top: 0.7rem;
}

.feedback {
  margin: 0.85rem 0 0;
  color: var(--color-accent-strong);
}

.no-entries {
  margin-top: 0.8rem;
}

.scope-board {
  margin-top: 1rem;
}

.scope-title {
  margin: 0 0 0.55rem;
  font-size: 1rem;
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
  gap: 0.35rem;
}

.lesson-tile {
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-sm);
  background: color-mix(in srgb, var(--color-accent-soft) 75%, white);
  padding: 0.45rem;
}

.lesson-title,
.lesson-meta {
  margin: 0;
}

.lesson-title {
  font-weight: 700;
}

.lesson-meta {
  margin-top: 0.2rem;
  color: var(--color-text-muted);
  font-size: 0.84rem;
}

.empty-slot {
  color: var(--color-text-muted);
}

@media (max-width: 1100px) {
  .management-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 900px) {
  .controls-grid,
  .pair-grid,
  .edit-grid {
    grid-template-columns: 1fr;
  }
}
</style>
