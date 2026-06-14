<script setup>
import { computed, reactive, ref } from 'vue';
import AppPageHeader from '../components/AppPageHeader.vue';
import EntityCrudPanel from '../components/admin/EntityCrudPanel.vue';
import { useSchoolAdminData } from '../composables/useSchoolAdminData';
import { createEntity } from '../services/schoolAdminRepository';

const { fetchEntity } = useSchoolAdminData();

const processSteps = [
  { key: 'classroom_type', title: 'Classroom Types', description: 'Create the classroom categories needed for subjects and rooms.' },
  { key: 'student_group', title: 'Student Groups', description: 'Create groups that will receive lesson allocations.' },
  { key: 'subjects', title: 'Subjects', description: 'Define subjects and assign required classroom type for each one.' },
  { key: 'classroom', title: 'Classrooms', description: 'Create physical rooms and connect each room to a classroom type.' },
  { key: 'teachers', title: 'Teachers', description: 'Create teachers and assign each teacher to a subject.' },
  { key: 'lesson_count', title: 'Lesson Hours', description: 'Set weekly hour allocations for every group-subject pair.' }
];

const draftState = reactive({
  classroom_type: [],
  student_group: [],
  subjects: [],
  classroom: [],
  teachers: [],
  lesson_count: []
});

const currentStepIndex = ref(0);
const feedback = ref('');
const isFinalizing = ref(false);
const draftIdCounter = ref(1);

function buildOptions(entities, { labelKey = 'name', labelFn = null } = {}) {
  return entities.map((entity) => ({
    value: entity.id,
    label: labelFn ? labelFn(entity) : entity[labelKey]
  }));
}

const entityDefinitions = computed(() => {
  const classroomTypeOptions = buildOptions(draftState.classroom_type);
  const studentGroupOptions = buildOptions(draftState.student_group);
  const subjectOptions = buildOptions(draftState.subjects);

  return {
    classroom_type: {
      title: 'Classroom Types',
      description: 'Create classroom type records for this setup process.',
      fields: [{ key: 'name', label: 'Name', type: 'text' }]
    },
    student_group: {
      title: 'Student Groups',
      description: 'Create student groups for this setup process.',
      fields: [{ key: 'name', label: 'Name', type: 'text' }]
    },
    subjects: {
      title: 'Subjects',
      description: 'Create subject records and map each one to a classroom type.',
      fields: [
        { key: 'name', label: 'Name', type: 'text' },
        { key: 'classroom_type_id', label: 'Classroom Type', type: 'select', options: classroomTypeOptions }
      ]
    },
    classroom: {
      title: 'Classrooms',
      description: 'Create classroom records and map each one to a classroom type.',
      fields: [
        { key: 'name', label: 'Name', type: 'text' },
        { key: 'classroom_type_id', label: 'Classroom Type', type: 'select', options: classroomTypeOptions }
      ]
    },
    teachers: {
      title: 'Teachers',
      description: 'Create teacher records and map each one to a subject.',
      fields: [
        { key: 'first_name', label: 'First Name', type: 'text' },
        { key: 'last_name', label: 'Last Name', type: 'text' },
        { key: 'subject_id', label: 'Subject', type: 'select', options: subjectOptions }
      ]
    },
    lesson_count: {
      title: 'Lesson Hours',
      description: 'Create weekly lesson hour allocations for groups and subjects.',
      fields: [
        { key: 'student_group_id', label: 'Student Group', type: 'select', options: studentGroupOptions },
        { key: 'subject_id', label: 'Subject', type: 'select', options: subjectOptions },
        { key: 'hours', label: 'Hours', type: 'number', min: 0 }
      ]
    }
  };
});

const currentStep = computed(() => processSteps[currentStepIndex.value]);
const currentDefinition = computed(() => entityDefinitions.value[currentStep.value.key]);
const currentRows = computed(() => draftState[currentStep.value.key]);
const isFirstStep = computed(() => currentStepIndex.value === 0);
const isLastStep = computed(() => currentStepIndex.value === processSteps.length - 1);

function getStepStatus(index) {
  if (index < currentStepIndex.value) {
    return 'done';
  }
  if (index === currentStepIndex.value) {
    return 'current';
  }
  return 'upcoming';
}

function createDraftId() {
  const id = `draft-${draftIdCounter.value}`;
  draftIdCounter.value += 1;
  return id;
}

function clearStepData(stepKey) {
  draftState[stepKey] = [];
}

function resetProcess() {
  processSteps.forEach((step) => {
    clearStepData(step.key);
  });
  currentStepIndex.value = 0;
  draftIdCounter.value = 1;
}

function requireCurrentStepRecords() {
  if (currentRows.value.length > 0) {
    return true;
  }

  feedback.value = `Add at least one ${currentDefinition.value.title.toLowerCase()} entry before continuing.`;
  return false;
}

function goToNextStep() {
  if (isLastStep.value || !requireCurrentStepRecords()) {
    return;
  }

  currentStepIndex.value += 1;
  feedback.value = '';
}

function goToPreviousStep() {
  if (isFirstStep.value) {
    return;
  }

  const step = currentStep.value;
  const hasRecords = draftState[step.key].length > 0;
  if (hasRecords) {
    const accepted = confirm(
      `Going back will delete all records from "${step.title}" in this setup process. Continue?`
    );
    if (!accepted) {
      return;
    }

    clearStepData(step.key);
  }

  currentStepIndex.value -= 1;
  feedback.value = '';
}

function resolveMappedId(mapping, draftId, relationLabel) {
  const resolvedId = mapping.get(draftId);
  if (!resolvedId) {
    throw new Error(`Cannot finalize setup because a ${relationLabel} reference is invalid.`);
  }
  return resolvedId;
}

async function handleFinalize() {
  if (!isLastStep.value || !requireCurrentStepRecords()) {
    return;
  }

  isFinalizing.value = true;
  feedback.value = '';

  try {
    const classroomTypeIdMap = new Map();
    const studentGroupIdMap = new Map();
    const subjectIdMap = new Map();

    for (const classroomType of draftState.classroom_type) {
      const created = await createEntity('classroom_type', { name: classroomType.name });
      classroomTypeIdMap.set(classroomType.id, created.id);
    }

    for (const studentGroup of draftState.student_group) {
      const created = await createEntity('student_group', { name: studentGroup.name });
      studentGroupIdMap.set(studentGroup.id, created.id);
    }

    for (const subject of draftState.subjects) {
      const classroomTypeId = resolveMappedId(
        classroomTypeIdMap,
        subject.classroom_type_id,
        'classroom type'
      );
      const created = await createEntity('subjects', {
        name: subject.name,
        classroom_type_id: Number(classroomTypeId)
      });
      subjectIdMap.set(subject.id, created.id);
    }

    for (const classroom of draftState.classroom) {
      const classroomTypeId = resolveMappedId(
        classroomTypeIdMap,
        classroom.classroom_type_id,
        'classroom type'
      );
      await createEntity('classroom', {
        name: classroom.name,
        classroom_type_id: Number(classroomTypeId)
      });
    }

    for (const teacher of draftState.teachers) {
      const subjectId = resolveMappedId(subjectIdMap, teacher.subject_id, 'subject');
      await createEntity('teachers', {
        first_name: teacher.first_name,
        last_name: teacher.last_name,
        subject_id: Number(subjectId)
      });
    }

    for (const lessonCount of draftState.lesson_count) {
      const studentGroupId = resolveMappedId(
        studentGroupIdMap,
        lessonCount.student_group_id,
        'student group'
      );
      const subjectId = resolveMappedId(subjectIdMap, lessonCount.subject_id, 'subject');
      await createEntity('lesson_count', {
        student_group_id: Number(studentGroupId),
        subject_id: Number(subjectId),
        hours: Number(lessonCount.hours)
      });
    }

    await Promise.all([
      fetchEntity('classroom_type'),
      fetchEntity('student_group'),
      fetchEntity('subjects'),
      fetchEntity('classroom'),
      fetchEntity('teachers'),
      fetchEntity('lesson_count')
    ]);

    const totalRecords = processSteps.reduce((sum, step) => sum + draftState[step.key].length, 0);
    resetProcess();
    feedback.value = `Setup finalized. ${totalRecords} records were saved to the database.`;
  } catch (error) {
    feedback.value = error.message || 'Failed to finalize setup process.';
  } finally {
    isFinalizing.value = false;
  }
}

function handleCreate({ entityName, payload }) {
  if (entityName !== currentStep.value.key) {
    return;
  }

  draftState[entityName].push({
    id: createDraftId(),
    ...payload
  });
  feedback.value = `${currentDefinition.value.title}: draft entry added.`;
}

function handleEdit({ entityName, entityId, payload }) {
  if (entityName !== currentStep.value.key) {
    return;
  }

  const rowIndex = draftState[entityName].findIndex((row) => row.id === entityId);
  if (rowIndex < 0) {
    feedback.value = 'Entry not found for editing.';
    return;
  }

  draftState[entityName][rowIndex] = {
    ...draftState[entityName][rowIndex],
    ...payload
  };
  feedback.value = `${currentDefinition.value.title}: draft entry updated.`;
}

function handleDelete({ entityName, entityId }) {
  if (entityName !== currentStep.value.key) {
    return;
  }

  const rowIndex = draftState[entityName].findIndex((row) => row.id === entityId);
  if (rowIndex < 0) {
    feedback.value = 'Entry not found for deletion.';
    return;
  }

  draftState[entityName].splice(rowIndex, 1);
  feedback.value = `${currentDefinition.value.title}: draft entry deleted.`;
}
</script>

<template>
  <section class="wizard-layout">
    <AppPageHeader
      title="Guided Data Setup"
      description="Complete all core records in a dependency-safe sequence, then submit everything to the backend in one final step."
    />

    <article class="card">
      <div class="wizard-head">
        <h2 class="section-title">Setup Progress</h2>
        <p class="muted wizard-progress-text">
          Step {{ currentStepIndex + 1 }} of {{ processSteps.length }}: {{ currentStep.title }}
        </p>
      </div>

      <ol class="wizard-steps" aria-label="Guided setup steps">
        <li
          v-for="(step, index) in processSteps"
          :key="step.key"
          class="wizard-step"
          :class="`is-${getStepStatus(index)}`"
        >
          <span class="wizard-step-index">{{ index + 1 }}</span>
          <div>
            <p class="wizard-step-title">{{ step.title }}</p>
            <p class="muted wizard-step-meta">Draft records: {{ draftState[step.key].length }}</p>
          </div>
        </li>
      </ol>
    </article>

    <p v-if="feedback" class="card feedback">{{ feedback }}</p>

    <EntityCrudPanel
      :entity-name="currentStep.key"
      :title="currentDefinition.title"
      :description="currentDefinition.description"
      :fields="currentDefinition.fields"
      :rows="currentRows"
      :busy="isFinalizing"
      @create="handleCreate"
      @edit="handleEdit"
      @delete="handleDelete"
    />

    <article class="card wizard-actions">
      <p class="muted action-hint">
        Going back removes records from your current category after confirmation.
      </p>

      <div class="action-buttons">
        <button type="button" class="btn" :disabled="isFirstStep || isFinalizing" @click="goToPreviousStep">
          Previous Category
        </button>
        <button
          v-if="!isLastStep"
          type="button"
          class="btn btn-primary"
          :disabled="isFinalizing"
          @click="goToNextStep"
        >
          Next Category
        </button>
        <button
          v-else
          type="button"
          class="btn btn-primary"
          :disabled="isFinalizing"
          @click="handleFinalize"
        >
          {{ isFinalizing ? 'Finalizing...' : 'Finalize and Save' }}
        </button>
      </div>
    </article>
  </section>
</template>

<style scoped>
.wizard-layout {
  display: grid;
  gap: 1rem;
}

.wizard-head {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem 1rem;
}

.wizard-head .section-title {
  margin: 0;
}

.wizard-progress-text {
  margin: 0;
}

.wizard-steps {
  margin: 0.85rem 0 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 0.55rem;
}

.wizard-step {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 0.55rem 0.65rem;
  background: var(--color-surface-2);
  display: grid;
  grid-template-columns: 1.8rem 1fr;
  gap: 0.65rem;
  align-items: center;
}

.wizard-step-index {
  width: 1.8rem;
  height: 1.8rem;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--color-border-strong);
  font-size: 0.88rem;
  font-weight: 700;
}

.wizard-step-title {
  margin: 0;
  font-weight: 600;
}

.wizard-step-meta {
  margin: 0.1rem 0 0;
  font-size: 0.85rem;
}

.wizard-step.is-current {
  border-color: var(--color-accent);
  background: var(--color-accent-soft);
}

.wizard-step.is-current .wizard-step-index {
  border-color: var(--color-accent-strong);
  color: var(--color-accent-strong);
}

.wizard-step.is-done {
  border-color: color-mix(in srgb, var(--color-accent) 55%, white);
}

.feedback {
  margin: 0;
  border-left: 4px solid var(--color-accent);
}

.wizard-actions {
  display: grid;
  gap: 0.75rem;
}

.action-hint {
  margin: 0;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
}
</style>
