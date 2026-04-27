<script setup>
import { computed, onMounted, ref } from 'vue';
import AppPageHeader from '../components/AppPageHeader.vue';
import EntityCrudPanel from '../components/admin/EntityCrudPanel.vue';
import { useSchoolAdminData } from '../composables/useSchoolAdminData';

const {
  state,
  isLoading,
  ensureLoaded,
  addEntity
} = useSchoolAdminData();

const activeTab = ref('teachers');
const feedback = ref('');

onMounted(async () => {
  await ensureLoaded();
});

// Helper to map entities to dropdown options
function buildOptions(entities, { valueKey = 'id', labelKey = 'name', labelFn = null } = {}) {
  return entities.map((entity) => ({
    value: entity[valueKey],
    label: labelFn ? labelFn(entity) : entity[labelKey]
  }));
}

const entityDefinitions = computed(() => {
  const subjectOptions = buildOptions(state.subjects);
  const teacherOptions = buildOptions(state.teachers, {
    valueKey: 'id',
    labelFn: (t) => `${t.first_name} ${t.last_name}`
  });
  const groupOptions = buildOptions(state.classGroups);
  const roomOptions = buildOptions(state.classRooms);

  return {
    teachers: {
      title: 'Teachers',
      description: 'Create teaching staff records linked to subjects.',
      fields: [
        { key: 'first_name', label: 'First Name', type: 'text' },
        { key: 'last_name', label: 'Last Name', type: 'text' },
        { key: 'subject_id', label: 'Subject', type: 'select', options: subjectOptions }
      ]
    },
    classGroups: {
      title: 'Class Groups',
      description: 'Create class groups that receive timetables.',
      fields: [{ key: 'name', label: 'Name', type: 'text' }]
    },
    classRooms: {
      title: 'Class Rooms',
      description: 'Create rooms used by scheduled classes.',
      fields: [{ key: 'name', label: 'Name', type: 'text' }]
    },
    subjects: {
      title: 'Subjects',
      description: 'Create curriculum subjects used in classes.',
      fields: [{ key: 'name', label: 'Name', type: 'text' }]
    },
    classes: {
      title: 'Classes',
      description: 'Define class assignments linking groups, teachers, rooms, and dates.',
      fields: [
        { key: 'subject_id', label: 'Subject', type: 'select', options: subjectOptions },
        { key: 'classroom_id', label: 'Class Room', type: 'select', options: roomOptions },
        { key: 'teacher_id', label: 'Teacher', type: 'select', options: teacherOptions },
        { key: 'group_id', label: 'Class Group', type: 'select', options: groupOptions },
        { key: 'start_time', label: 'Start Time', type: 'datetime-local' },
        { key: 'end_time', label: 'End Time', type: 'datetime-local' },
        { key: 'description', label: 'Description', type: 'text' }
      ]
    }
  };
});

const currentDefinition = computed(() => entityDefinitions.value[activeTab.value]);
const currentRows = computed(() => state[activeTab.value]);

async function handleCreate({ entityName, payload }) {
  feedback.value = '';

  try {
    await addEntity(entityName, payload);
    feedback.value = `${entityDefinitions.value[entityName].title}: new entry added.`;
  } catch (error) {
    feedback.value = error.message;
  }
}
</script>

<template>
  <section class="admin-data-layout">
    <AppPageHeader
      title="Administrator Data Management"
      description="Create teachers, groups, rooms, subjects, and classes from one operational workspace."
    />

    <article class="card">
      <div class="tabs" role="tablist" aria-label="Entity tables">
        <button
          v-for="(definition, key) in entityDefinitions"
          :key="key"
          type="button"
          class="btn tab-btn"
          :class="{ 'is-active': activeTab === key }"
          role="tab"
          :aria-selected="activeTab === key"
          @click="activeTab = key"
        >
          {{ definition.title }}
        </button>
      </div>
      <p class="muted tab-hint">Use the tabs to create and review master data entries.</p>
    </article>

    <p v-if="feedback" class="card feedback">{{ feedback }}</p>

    <EntityCrudPanel
      :entity-name="activeTab"
      :title="currentDefinition.title"
      :description="currentDefinition.description"
      :fields="currentDefinition.fields"
      :rows="currentRows"
      :busy="isLoading"
      @create="handleCreate"
    />
  </section>
</template>

<style scoped>
.admin-data-layout {
  display: grid;
  gap: 1rem;
}

.tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tab-btn.is-active {
  border-color: var(--color-accent);
  background: var(--color-accent-soft);
  color: var(--color-accent-strong);
}

.tab-hint {
  margin: 0.75rem 0 0;
}

.feedback {
  margin: 0;
  border-left: 4px solid var(--color-accent);
}
</style>
