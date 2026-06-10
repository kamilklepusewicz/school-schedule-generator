<script setup>
import { computed, onMounted, ref } from 'vue';
import AppPageHeader from '../components/AppPageHeader.vue';
import EntityCrudPanel from '../components/admin/EntityCrudPanel.vue';
import LessonCountPanel from '../components/admin/LessonCountPanel.vue';
import { useSchoolAdminData } from '../composables/useSchoolAdminData';

const {
  state,
  isLoading,
  ensureLoaded,
  addEntity,
  editEntity,
  removeEntity,
  saveBulkLessonCounts,
  fetchEntity
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

// Helper to format day number to day name
function formatDayName(dayNumber) {
  const days = ['', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
  return days[dayNumber] || `Day ${dayNumber}`;
}

// Helper to format hour to time format
function formatHour(hour) {
  return `${String(hour).padStart(2, '0')}:00`;
}

// Dependency checks
const hasDependencyIssues = computed(() => ({
  classroom: state.classroom_type.length === 0,
  subjects: state.classroom_type.length === 0,
  classes: state.subjects.length === 0 || state.classroom.length === 0 || state.teachers.length === 0 || state.student_group.length === 0,
  lesson_count: state.student_group.length === 0 || state.subjects.length === 0
}));

const entityDefinitions = computed(() => {
  const subjectOptions = buildOptions(state.subjects);
  const teacherOptions = buildOptions(state.teachers, {
    valueKey: 'id',
    labelFn: (t) => `${t.first_name} ${t.last_name}`
  });
  const studentGroupOptions = buildOptions(state.student_group);
  const classroomOptions = buildOptions(state.classroom);
  const classroomTypeOptions = buildOptions(state.classroom_type);
  
  // Day options for select dropdown
  const dayOptions = [
    { value: 1, label: 'Monday' },
    { value: 2, label: 'Tuesday' },
    { value: 3, label: 'Wednesday' },
    { value: 4, label: 'Thursday' },
    { value: 5, label: 'Friday' }
  ];
  
  // Hour options for select dropdown
  const hourOptions = Array.from({ length: 13 }, (_, i) => {
    const hour = i + 8;
    return { value: hour, label: `${String(hour).padStart(2, '0')}:00` };
  });

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
    student_group: {
      title: 'Student Groups',
      description: 'Create student groups that receive timetables.',
      fields: [{ key: 'name', label: 'Name', type: 'text' }]
    },
    classroom: {
      title: 'Classrooms',
      description: 'Create rooms used by scheduled classes.',
      fields: [
        { key: 'name', label: 'Name', type: 'text' },
        { key: 'classroom_type_id', label: 'Classroom Type', type: 'select', options: classroomTypeOptions }
      ],
      dependsOn: 'classroom_type',
      missingMessage: 'No classroom types available. Create at least one classroom type first.'
    },
    subjects: {
      title: 'Subjects',
      description: 'Create curriculum subjects used in classes.',
      fields: [
        { key: 'name', label: 'Name', type: 'text' },
        { key: 'classroom_type_id', label: 'Classroom Type', type: 'select', options: classroomTypeOptions }
      ],
      dependsOn: 'classroom_type',
      missingMessage: 'No classroom types available. Create at least one classroom type first.'
    },
    classes: {
      title: 'Classes',
      description: 'View, add, edit, and delete manual timetable classes.',
      fields: [
        { key: 'subject_id', label: 'Subject', type: 'select', options: subjectOptions },
        { key: 'classroom_id', label: 'Classroom', type: 'select', options: classroomOptions },
        { key: 'teacher_id', label: 'Teacher', type: 'select', options: teacherOptions },
        { key: 'group_id', label: 'Student Group', type: 'select', options: studentGroupOptions },
        { key: 'day', label: 'Day of Week', type: 'select', options: dayOptions },
        { key: 'start', label: 'Start Hour', type: 'select', options: hourOptions }
      ],
      missingMessage: 'Cannot create classes. Ensure you have subjects, classrooms, teachers, and student groups.'
    },
    classroom_type: {
      title: 'Classroom Types',
      description: 'Manage different types of classrooms (e.g., Lab, Lecture Hall, etc.).',
      fields: [{ key: 'name', label: 'Name', type: 'text' }]
    },
    lesson_count: {
      title: 'Lesson Hours',
      description: 'Set the number of hours for each subject per student group.',
      fields: [
        { key: 'student_group_id', label: 'Student Group', type: 'select', options: studentGroupOptions },
        { key: 'subject_id', label: 'Subject', type: 'select', options: subjectOptions },
        { key: 'hours', label: 'Hours', type: 'number', min: 0 }
      ],
      missingMessage: 'Cannot create lesson hours. Ensure you have student groups and subjects.'
    }
  };
});

const currentDefinition = computed(() => entityDefinitions.value[activeTab.value]);
const currentRows = computed(() => state[activeTab.value]);
const isClassesTab = computed(() => activeTab.value === 'classes');

async function handleCreate({ entityName, payload }) {
  feedback.value = '';

  try {
    await addEntity(entityName, payload);
    feedback.value = `${entityDefinitions.value[entityName].title}: new entry added.`;
  } catch (error) {
    feedback.value = error.message;
  }
}

async function handleEdit({ entityName, entityId, payload }) {
  feedback.value = '';

  try {
    await editEntity(entityName, entityId, payload);
    feedback.value = `${entityDefinitions.value[entityName].title}: entry updated successfully.`;
  } catch (error) {
    feedback.value = error.message;
  }
}

async function handleDelete({ entityName, entityId }) {
  try {
    await removeEntity(entityName, entityId);
    feedback.value = `${entityDefinitions.value[entityName].title}: entry deleted successfully.`;
  } catch (error) {
    feedback.value = error.message;
  }
}

async function handleSaveLessonCounts({ studentGroupId, lessonCounts }) {
  feedback.value = '';

  try {
    // Send all lesson counts as a single batch request
    const formattedData = lessonCounts.map((item) => ({
      id: item.id,
      student_group_id: item.student_group_id,
      subject_id: item.subject_id,
      hours: Number(item.hours)
    }));

    await saveBulkLessonCounts(formattedData);

    // Refresh lesson_count data from backend
    await fetchEntity('lesson_count');

    const groupName = state.student_group.find((g) => g.id === studentGroupId)?.name;
    feedback.value = `Lesson hours updated successfully for ${groupName}.`;
  } catch (error) {
    feedback.value = error.message;
  }
}

function switchToTab(tabName) {
  activeTab.value = tabName;
  feedback.value = '';
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

    <article v-if="currentDefinition.missingMessage && hasDependencyIssues[activeTab]" class="card warning-box">
      <p class="warning-title">⚠️ Missing Requirements</p>
      <p class="warning-text">{{ currentDefinition.missingMessage }}</p>
      <div v-if="currentDefinition.dependsOn" class="warning-actions">
        <button class="btn btn-small" @click="switchToTab(currentDefinition.dependsOn)">
          Go to {{ entityDefinitions[currentDefinition.dependsOn].title }}
        </button>
      </div>
    </article>

    <article v-if="isClassesTab" class="card info-box">
      <p class="warning-title">Classes View</p>
      <p class="warning-text">
        This table shows the classes stored in the backend timetable. You can add, edit, or delete rows directly here.
      </p>
    </article>

    <EntityCrudPanel
      v-if="activeTab !== 'lesson_count'"
      :entity-name="activeTab"
      :title="currentDefinition.title"
      :description="currentDefinition.description"
      :fields="currentDefinition.fields"
      :rows="currentRows"
      :busy="isLoading"
      @create="handleCreate"
      @edit="handleEdit"
      @delete="handleDelete"
    />

    <LessonCountPanel
      v-if="activeTab === 'lesson_count'"
      :student-groups="state.student_group"
      :subjects="state.subjects"
      :lesson-counts="state.lesson_count"
      :busy="isLoading"
      @save="handleSaveLessonCounts"
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

.warning-box {
  margin: 0;
  border-left: 4px solid var(--color-warning);
  background: var(--color-warning-soft, rgba(255, 193, 7, 0.1));
}

.warning-title {
  margin: 0 0 0.5rem 0;
  font-weight: 600;
  color: var(--color-warning, #ffc107);
}

.warning-text {
  margin: 0 0 0.75rem 0;
  color: var(--color-text);
}

.warning-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-small {
  padding: 0.35rem 0.75rem;
  font-size: 0.875rem;
}
</style>
