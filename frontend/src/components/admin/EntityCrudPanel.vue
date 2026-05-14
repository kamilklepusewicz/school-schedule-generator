<script setup>
import { computed, reactive, ref, watch } from 'vue';

const props = defineProps({
  entityName: {
    type: String,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  },
  fields: {
    type: Array,
    required: true
  },
  rows: {
    type: Array,
    default: () => []
  },
  busy: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['create', 'edit', 'delete']);

const formState = reactive({});
const editingId = ref(null);
const pageSizeOptions = [10, 20, 50];
const selectedPageSize = ref(pageSizeOptions[0]);
const displayedCount = ref(pageSizeOptions[0]);

function getDefaultValue(field) {
  if (field.type === 'number') {
    return field.key === 'hours' ? 0 : 0;
  }
  return '';
}

function resetForm() {
  props.fields.forEach((field) => {
    formState[field.key] = getDefaultValue(field);
  });
}

watch(
  () => props.entityName,
  () => {
    resetForm();
    displayedCount.value = selectedPageSize.value;
  },
  { immediate: true }
);

watch(
  () => props.rows.length,
  () => {
    if (displayedCount.value > props.rows.length) {
      displayedCount.value = props.rows.length;
    }
  }
);

const hasRows = computed(() => props.rows.length > 0);
const visibleRows = computed(() => props.rows.slice(0, displayedCount.value));
const hasMoreRows = computed(() => displayedCount.value < props.rows.length);

function onPageSizeChange() {
  displayedCount.value = Math.min(selectedPageSize.value, props.rows.length);
}

function loadNextRows() {
  displayedCount.value = Math.min(
    displayedCount.value + selectedPageSize.value,
    props.rows.length
  );
}

function displayValue(row, field) {
  const raw = row[field.key];

  if (field.type === 'select' && field.options?.length) {
    const option = field.options.find((item) => item.value === raw);
    return option ? option.label : '-';
  }

  // Format day of week
  if (field.key === 'day' && typeof raw === 'number') {
    const days = ['', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    return days[raw] || `-`;
  }

  // Format start hour
  if (field.key === 'start' && typeof raw === 'number') {
    return `${String(raw).padStart(2, '0')}:00`;
  }

  return raw;
}

function normalizePayload() {
  const payload = {};

  props.fields.forEach((field) => {
    const value = formState[field.key];
    payload[field.key] = field.type === 'number' ? Number(value) : value;
  });

  return payload;
}

function submitForm() {
  if (editingId.value) {
    emit('edit', {
      entityName: props.entityName,
      entityId: editingId.value,
      payload: normalizePayload()
    });
    editingId.value = null;
  } else {
    emit('create', {
      entityName: props.entityName,
      payload: normalizePayload()
    });
  }
}

function startEdit(row) {
  editingId.value = row.id;
  props.fields.forEach((field) => {
    formState[field.key] = row[field.key];
  });
}

function cancelEdit() {
  editingId.value = null;
  resetForm();
}

function deleteRow(rowId) {
  if (confirm('Are you sure you want to delete this entry?')) {
    emit('delete', {
      entityName: props.entityName,
      entityId: rowId
    });
  }
}
</script>

<template>
  <section class="entity-panel">
    <article class="card">
      <div class="panel-header">
        <div>
          <h2 class="section-title">{{ title }}</h2>
          <p class="muted">{{ description }}</p>
        </div>
        <span class="entry-count">Entries: {{ rows.length }}</span>
      </div>

      <form class="form-grid" @submit.prevent="submitForm">
        <label v-for="field in fields" :key="field.key" class="field">
          <span class="label-text">{{ field.label }}</span>

          <select v-if="field.type === 'select'" v-model="formState[field.key]" class="control">
            <option value="">Select...</option>
            <option
              v-for="option in field.options || []"
              :key="option.value"
              :value="option.value"
            >
              {{ option.label }}
            </option>
          </select>

          <input
            v-else
            v-model="formState[field.key]"
            :type="field.type === 'number' ? 'number' : field.type"
            class="control"
            :min="field.min"
            :max="field.max"
            :required="field.required !== false"
          />
        </label>

        <div class="actions-row">
          <button type="submit" class="btn btn-primary" :disabled="busy">
            {{ editingId ? 'Update Entry' : 'Add Entry' }}
          </button>
          <button type="button" class="btn" :disabled="busy" @click="editingId ? cancelEdit() : resetForm">
            {{ editingId ? 'Cancel' : 'Reset' }}
          </button>
        </div>
      </form>
      <p v-if="editingId" class="editing-note">Editing entry ID: {{ editingId }}</p>
    </article>

    <article class="card">
      <div class="table-header-row">
        <h3 class="section-title">{{ title }} Table</h3>

        <label class="field rows-per-page-control">
          <span class="label-text">Rows per load</span>
          <select v-model.number="selectedPageSize" class="control" @change="onPageSizeChange">
            <option v-for="size in pageSizeOptions" :key="size" :value="size">{{ size }}</option>
          </select>
        </label>
      </div>

      <p v-if="!hasRows" class="muted">No records yet. Add your first entry using the form.</p>

      <p v-else class="muted table-status">
        Showing {{ visibleRows.length }} of {{ rows.length }} records.
      </p>

      <div v-if="hasRows" class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th v-for="field in fields" :key="field.key">{{ field.label }}</th>
              <th class="actions-col">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in visibleRows" :key="row.id">
              <td v-for="field in fields" :key="field.key">{{ displayValue(row, field) }}</td>
              <td class="actions-col">
                <button class="btn btn-small btn-edit" :disabled="busy" @click="startEdit(row)" title="Edit">
                  ✎
                </button>
                <button class="btn btn-small btn-delete" :disabled="busy" @click="deleteRow(row.id)" title="Delete">
                  ✕
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="hasRows && hasMoreRows" class="table-footer-actions">
        <button type="button" class="btn" :disabled="busy" @click="loadNextRows">
          Load Next {{ selectedPageSize }}
        </button>
      </div>
    </article>
  </section>
</template>

<style scoped>
.entity-panel {
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

.table-header-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.table-header-row .section-title {
  margin: 0;
}

.rows-per-page-control {
  min-width: 140px;
  margin: 0;
}

.table-status {
  margin-top: 0.65rem;
}

.table-footer-actions {
  margin-top: 0.75rem;
}

.panel-header .muted {
  margin: 0;
}

.entry-count {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface-2);
  padding: 0.35rem 0.65rem;
  color: var(--color-text-muted);
}

.editing-note {
  margin-top: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--color-accent-soft);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  color: var(--color-accent-strong);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.actions-row {
  grid-column: 1 / -1;
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
}

.actions-col {
  width: 90px;
  text-align: center;
}

.btn-small {
  padding: 0.35rem 0.55rem;
  font-size: 0.875rem;
  min-width: auto;
}

.btn-edit {
  border-color: var(--color-accent);
  color: var(--color-accent-strong);
}

.btn-edit:hover:not(:disabled) {
  background: var(--color-accent-soft);
}

.btn-delete {
  border-color: var(--color-danger, #ff4757);
  color: var(--color-danger, #ff4757);
}

.btn-delete:hover:not(:disabled) {
  background: rgba(255, 71, 87, 0.1);
}

@media (max-width: 900px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
