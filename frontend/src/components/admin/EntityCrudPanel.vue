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

const emit = defineEmits(['create', 'update', 'delete']);

const formState = reactive({});
const mode = reactive({ type: 'create', id: null });
const pageSizeOptions = [10, 20, 50];
const selectedPageSize = ref(pageSizeOptions[0]);
const displayedCount = ref(pageSizeOptions[0]);

function getDefaultValue(field) {
  if (field.type === 'number') {
    return 0;
  }
  return '';
}

function resetForm() {
  props.fields.forEach((field) => {
    formState[field.key] = getDefaultValue(field);
  });
  mode.type = 'create';
  mode.id = null;
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
  const payload = normalizePayload();

  if (mode.type === 'edit') {
    emit('update', {
      entityName: props.entityName,
      id: mode.id,
      payload
    });
    return;
  }

  emit('create', {
    entityName: props.entityName,
    payload
  });
}

function loadRowForEdit(row) {
  props.fields.forEach((field) => {
    formState[field.key] = row[field.key];
  });

  mode.type = 'edit';
  mode.id = row.id;
}

function onDelete(rowId) {
  emit('delete', {
    entityName: props.entityName,
    id: rowId
  });

  if (mode.id === rowId) {
    resetForm();
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
            :required="field.required !== false"
          />
        </label>

        <div class="actions-row">
          <button type="submit" class="btn btn-primary" :disabled="busy">
            {{ mode.type === 'edit' ? 'Save Changes' : 'Add Entry' }}
          </button>
          <button type="button" class="btn" :disabled="busy" @click="resetForm">Reset</button>
        </div>
      </form>
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
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in visibleRows" :key="row.id">
              <td v-for="field in fields" :key="field.key">{{ displayValue(row, field) }}</td>
              <td>
                <div class="row-actions">
                  <button type="button" class="btn" :disabled="busy" @click="loadRowForEdit(row)">
                    Edit
                  </button>
                  <button type="button" class="btn btn-danger" :disabled="busy" @click="onDelete(row.id)">
                    Delete
                  </button>
                </div>
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

.row-actions {
  display: flex;
  gap: 0.45rem;
}

.btn-danger {
  border-color: var(--color-danger);
  color: var(--color-danger);
  background: color-mix(in srgb, var(--color-danger) 8%, white);
}

@media (max-width: 900px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
