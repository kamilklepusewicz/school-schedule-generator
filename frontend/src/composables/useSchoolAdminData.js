// SECTION: Imports
import { computed, reactive, ref } from 'vue';
import {
  createEntity,
  generateTimetables,
  listEntities,
  listTimetableEntries,
  listTimetableGroups,
  swapTimetableEntries,
  updateTimetableEntry,
} from '../services/schoolAdminRepository';

// SECTION: Shared Reactive State
const state = reactive({
  teachers: [],
  classGroups: [],
  classRooms: [],
  subjects: [],
  classes: [],
  timetableGroups: [],
  timetableEntries: []
});

// SECTION: Entity Configuration
const entityKeys = ['teachers', 'classGroups', 'classRooms', 'subjects', 'classes'];

// SECTION: Request Status Flags
const isLoading = ref(false);
const isInitialized = ref(false);
const lastGenerationRequest = ref(null);

// SECTION: Utility Helper for Loading State Management
async function withLoading(asyncFn) {
  isLoading.value = true;
  try {
    return await asyncFn();
  } finally {
    isLoading.value = false;
  }
}

// SECTION: Data Loading Helpers
async function fetchEntity(entityName) {
  state[entityName] = await listEntities(entityName);
}

async function ensureLoaded() {
  if (isInitialized.value) {
    return;
  }

  await withLoading(async () => {
    await Promise.all(entityKeys.map((entityName) => fetchEntity(entityName)));
    state.timetableGroups = await listTimetableGroups();
    isInitialized.value = true;
  });
}

async function fetchTimetableGroups() {
  state.timetableGroups = await listTimetableGroups();
}

async function fetchTimetableEntries(groupId) {
  state.timetableEntries = await listTimetableEntries(groupId);
}

// SECTION: Entity Mutation Operations
async function addEntity(entityName, payload) {
  await withLoading(async () => {
    await createEntity(entityName, payload);
    await fetchEntity(entityName);
  });
}

// SECTION: Timetable Operations
async function requestTimetableGeneration(payload) {
  return await withLoading(async () => {
    const response = await generateTimetables(payload);
    await fetchTimetableGroups();
    lastGenerationRequest.value = response;
    return response;
  });
}

async function moveTimetableEntry(groupId, entryId, payload) {
  await withLoading(async () => {
    await updateTimetableEntry(groupId, entryId, payload);
    await fetchTimetableEntries(groupId);
  });
}

async function swapTimetableEntriesById(groupId, firstId, secondId) {
  await withLoading(async () => {
    await swapTimetableEntries(groupId, firstId, secondId);
    await fetchTimetableEntries(groupId);
  });
}

const dashboardStats = computed(() => [
  { key: 'teachers', label: 'Teachers', value: state.teachers.length },
  { key: 'classGroups', label: 'Class Groups', value: state.classGroups.length },
  { key: 'classRooms', label: 'Class Rooms', value: state.classRooms.length },
  { key: 'subjects', label: 'Subjects', value: state.subjects.length },
  { key: 'classes', label: 'Classes', value: state.classes.length },
  { key: 'timetableGroups', label: 'Timetable Groups', value: state.timetableGroups.length }
]);

// SECTION: Public Composable API
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
    requestTimetableGeneration,
    moveTimetableEntry,
    swapTimetableEntriesById
  };
}