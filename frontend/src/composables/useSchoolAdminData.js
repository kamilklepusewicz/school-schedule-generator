import { computed, reactive, ref } from 'vue';
import {
  createEntity,
  deleteEntity,
  generateTimetables,
  listEntities,
  listTimetableEntries,
  listTimetableGroups,
  swapTimetableEntries,
  updateTimetableEntry,
  updateEntity
} from '../services/schoolAdminRepository';

const state = reactive({
  teachers: [],
  classGroups: [],
  classRooms: [],
  subjects: [],
  classes: [],
  timetableGroups: [],
  timetableEntries: []
});

const entityKeys = ['teachers', 'classGroups', 'classRooms', 'subjects', 'classes'];

const isLoading = ref(false);
const isInitialized = ref(false);
const lastGenerationRequest = ref(null);

async function fetchEntity(entityName) {
  state[entityName] = await listEntities(entityName);
}

async function ensureLoaded() {
  if (isInitialized.value) {
    return;
  }

  isLoading.value = true;

  try {
    await Promise.all(entityKeys.map((entityName) => fetchEntity(entityName)));
    state.timetableGroups = await listTimetableGroups();
    isInitialized.value = true;
  } finally {
    isLoading.value = false;
  }
}

async function fetchTimetableGroups() {
  state.timetableGroups = await listTimetableGroups();
}

async function fetchTimetableEntries(groupId) {
  state.timetableEntries = await listTimetableEntries(groupId);
}

async function addEntity(entityName, payload) {
  isLoading.value = true;
  try {
    await createEntity(entityName, payload);
    await fetchEntity(entityName);
  } finally {
    isLoading.value = false;
  }
}

async function editEntity(entityName, id, payload) {
  isLoading.value = true;
  try {
    await updateEntity(entityName, id, payload);
    await fetchEntity(entityName);
  } finally {
    isLoading.value = false;
  }
}

async function removeEntity(entityName, id) {
  isLoading.value = true;
  try {
    await deleteEntity(entityName, id);
    await fetchEntity(entityName);
  } finally {
    isLoading.value = false;
  }
}

async function requestTimetableGeneration(payload) {
  isLoading.value = true;
  try {
    const response = await generateTimetables(payload);
    await fetchTimetableGroups();
    lastGenerationRequest.value = response;
    return response;
  } finally {
    isLoading.value = false;
  }
}

async function moveTimetableEntry(groupId, entryId, payload) {
  isLoading.value = true;
  try {
    await updateTimetableEntry(groupId, entryId, payload);
    await fetchTimetableEntries(groupId);
  } finally {
    isLoading.value = false;
  }
}

async function swapTimetableEntriesById(groupId, firstId, secondId) {
  isLoading.value = true;
  try {
    await swapTimetableEntries(groupId, firstId, secondId);
    await fetchTimetableEntries(groupId);
  } finally {
    isLoading.value = false;
  }
}

const dashboardStats = computed(() => [
  { key: 'teachers', label: 'Teachers', value: state.teachers.length },
  { key: 'classGroups', label: 'Class Groups', value: state.classGroups.length },
  { key: 'classRooms', label: 'Class Rooms', value: state.classRooms.length },
  { key: 'subjects', label: 'Subjects', value: state.subjects.length },
  { key: 'classes', label: 'Classes', value: state.classes.length },
  { key: 'timetableGroups', label: 'Timetable Groups', value: state.timetableGroups.length }
]);

export function useSchoolAdminData() {
  return {
    state,
    isLoading,
    lastGenerationRequest,
    dashboardStats,
    ensureLoaded,
    fetchEntity,
    fetchTimetableGroups,
    fetchTimetableEntries,
    addEntity,
    editEntity,
    removeEntity,
    requestTimetableGeneration,
    moveTimetableEntry,
    swapTimetableEntriesById
  };
}
