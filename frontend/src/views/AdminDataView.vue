<script setup>
import { computed, onMounted, ref } from 'vue';
import AppPageHeader from '../components/AppPageHeader.vue';
import EntityCrudPanel from '../components/admin/EntityCrudPanel.vue';
import { useSchoolAdminData } from '../composables/useSchoolAdminData';

const {
  state,
  isLoading,
  ensureLoaded,
  addEntity,
  editEntity,
  removeEntity
} = useSchoolAdminData();

const activeTab = ref('teachers');
const feedback = ref('');

onMounted(async () => {
  await ensureLoaded();
});

const entityDefinitions = computed(() => {
  const subjectOptions = state.subjects.map((subject) => ({
    value: subject.id,
    label: subject.name
  }));

  const teacherOptions = state.teachers.map((teacher) => ({
    value: teacher.id,
    label: `${teacher.firstName} ${teacher.lastName}`
  }));

  const groupOptions = state.classGroups.map((group) => ({
    value: group.id,
    label: group.name
  }));

  const roomOptions = state.classRooms.map((room) => ({
    value: room.id,
    label: `${room.number} ${room.name}`
  }));

  return {
    teachers: {
      title: 'Teachers',
      description: 'Manage teaching staff available for classes.',
      fields: [
        { key: 'firstName', label: 'First Name', type: 'text' },
        { key: 'lastName', label: 'Last Name', type: 'text' }
      ]
    },
    classGroups: {
      title: 'Class Groups',
      description: 'Manage student groups that receive timetables.',
      fields: [
        { key: 'name', label: 'Name', type: 'text' },
        { key: 'no_students', label: 'No. Students', type: 'number' }
      ]
    },
    classRooms: {
      title: 'Class Rooms',
      description: 'Manage available rooms and seating capacity.',
      fields: [
        { key: 'number', label: 'Room Number', type: 'text' },
        { key: 'name', label: 'Room Name', type: 'text' },
        { key: 'no_seats', label: 'No. Seats', type: 'number' }
      ]
    },
    subjects: {
      title: 'Subjects',
      description: 'Manage curriculum subjects used in classes.',
      fields: [{ key: 'name', label: 'Name', type: 'text' }]
    },
    classes: {
      title: 'Classes',
      description: 'Define class assignments linking groups, teachers, rooms, and dates.',
      fields: [
        { key: 'subject_id', label: 'Subject', type: 'select', options: subjectOptions },
        { key: 'teacher_id', label: 'Teacher', type: 'select', options: teacherOptions },
        { key: 'group_id', label: 'Group', type: 'select', options: groupOptions },
        { key: 'room_id', label: 'Room', type: 'select', options: roomOptions },
        { key: 'start_date', label: 'Start Date', type: 'datetime-local' },
        { key: 'end_date', label: 'End Date', type: 'datetime-local' }
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

async function handleUpdate({ entityName, id, payload }) {
  feedback.value = '';

  try {
    await editEntity(entityName, id, payload);
    feedback.value = `${entityDefinitions.value[entityName].title}: entry updated.`;
  } catch (error) {
    feedback.value = error.message;
  }
}

async function handleDelete({ entityName, id }) {
  feedback.value = '';

  try {
    await removeEntity(entityName, id);
    feedback.value = `${entityDefinitions.value[entityName].title}: entry deleted.`;
  } catch (error) {
    feedback.value = error.message;
  }
}
</script>

<template>
  <section class="admin-data-layout">
    <AppPageHeader
      title="Administrator Data Management"
      description="Manage teachers, groups, rooms, subjects, and classes from one operational workspace."
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
      <p class="muted tab-hint">Use the tab to view and edit teaching staff.</p>
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
      @update="handleUpdate"
      @delete="handleDelete"
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
