// SECTION: Imports
import {
  createMockEntity,
  deleteMockEntity,
  generateMockTimetables,
  listMockEntities,
  listMockTimetableEntries,
  listMockTimetableGroups,
  swapMockTimetableEntries,
  updateMockEntity,
  updateMockTimetableEntry
} from './mocks/schoolAdminMockRepository';

// SECTION: Runtime Configuration and Local Cache
const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');
const localTeacherOverrides = new Map();
const locallyDeletedTeacherIds = new Set();
const TEACHER_OVERRIDES_STORAGE_KEY = 'schoolAdmin.teacherOverrides';
const TEACHER_DELETIONS_STORAGE_KEY = 'schoolAdmin.teacherDeletions';

// SECTION: Browser Storage Utilities
function canUseStorage() {
  return typeof window !== 'undefined' && Boolean(window.localStorage);
}

function loadTeacherLocalChanges() {
  if (!canUseStorage()) {
    return;
  }

  try {
    const storedOverrides = window.localStorage.getItem(TEACHER_OVERRIDES_STORAGE_KEY);
    const storedDeletions = window.localStorage.getItem(TEACHER_DELETIONS_STORAGE_KEY);

    if (storedOverrides) {
      const parsedOverrides = JSON.parse(storedOverrides);
      Object.entries(parsedOverrides).forEach(([id, teacher]) => {
        localTeacherOverrides.set(id, teacher);
      });
    }

    if (storedDeletions) {
      const parsedDeletions = JSON.parse(storedDeletions);
      parsedDeletions.forEach((id) => locallyDeletedTeacherIds.add(id));
    }
  } catch {
    localTeacherOverrides.clear();
    locallyDeletedTeacherIds.clear();
  }
}

function persistTeacherLocalChanges() {
  if (!canUseStorage()) {
    return;
  }

  const serializedOverrides = Object.fromEntries(localTeacherOverrides.entries());
  const serializedDeletions = Array.from(locallyDeletedTeacherIds);

  window.localStorage.setItem(
    TEACHER_OVERRIDES_STORAGE_KEY,
    JSON.stringify(serializedOverrides)
  );
  window.localStorage.setItem(
    TEACHER_DELETIONS_STORAGE_KEY,
    JSON.stringify(serializedDeletions)
  );
}

loadTeacherLocalChanges();

// SECTION: HTTP Request Utilities
function buildApiUrl(path) {
  return `${API_BASE_URL}${path}`;
}

async function requestJson(path, options = {}) {
  let response;

  try {
    response = await fetch(buildApiUrl(path), {
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {})
      },
      ...options
    });
  } catch {
    throw new Error('Cannot connect to the backend API.');
  }

  if (!response.ok) {
    let message = `Request failed with status ${response.status}.`;

    try {
      const details = await response.json();
      if (details?.detail) {
        message = typeof details.detail === 'string'
          ? details.detail
          : JSON.stringify(details.detail);
      }
    } catch {
      // Fall back to the generic HTTP status message.
    }

    throw new Error(message);
  }

  return response.json();
}

// SECTION: API Data Mapping Utilities
function fromApiTeacher(teacher) {
  return {
    id: teacher.id,
    firstName: teacher.first_name,
    lastName: teacher.last_name
  };
}

function toApiTeacher(teacher) {
  return {
    first_name: teacher.firstName,
    last_name: teacher.lastName
  };
}

// SECTION: Generic Data Utilities
function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

// SECTION: Teacher Local Override Logic
function applyTeacherLocalChanges(teachers) {
  return teachers
    .filter((teacher) => !locallyDeletedTeacherIds.has(String(teacher.id)))
    .map((teacher) => {
      const override = localTeacherOverrides.get(String(teacher.id));
      return override
        ? {
          ...teacher,
          ...override
        }
        : teacher;
    });
}

// SECTION: Teacher Entity Handler
async function listTeachers() {
  const teachers = await requestJson('/teachers');
  return applyTeacherLocalChanges(teachers.map(fromApiTeacher));
}

async function createTeacher(payload) {
  const teacher = await requestJson('/teachers', {
    method: 'POST',
    body: JSON.stringify(toApiTeacher(payload))
  });

  const normalizedTeacher = fromApiTeacher(teacher);
  const teacherId = String(normalizedTeacher.id);
  localTeacherOverrides.delete(teacherId);
  locallyDeletedTeacherIds.delete(teacherId);
  persistTeacherLocalChanges();
  return normalizedTeacher;
}

async function updateTeacher(id, payload) {
  const teacherId = String(id);
  const existingTeacher = (await listTeachers())
    .find((teacher) => String(teacher.id) === teacherId);

  if (!existingTeacher) {
    throw new Error(`Entry with id "${id}" not found.`);
  }

  const nextTeacher = {
    ...existingTeacher,
    ...clone(payload)
  };

  localTeacherOverrides.set(teacherId, nextTeacher);
  locallyDeletedTeacherIds.delete(teacherId);
  persistTeacherLocalChanges();
  return clone(nextTeacher);
}

async function deleteTeacher(id) {
  const teacherId = String(id);
  const existingTeacher = (await listTeachers())
    .find((teacher) => String(teacher.id) === teacherId);

  if (!existingTeacher) {
    throw new Error(`Entry with id "${id}" not found.`);
  }

  locallyDeletedTeacherIds.add(teacherId);
  localTeacherOverrides.delete(teacherId);
  persistTeacherLocalChanges();
  return existingTeacher;
}

// SECTION: Entity Handler Registry
const defaultEntityHandler = {
  list: (entityName) => listMockEntities(entityName),
  create: (entityName, payload) => createMockEntity(entityName, payload),
  update: (entityName, id, payload) => updateMockEntity(entityName, id, payload),
  remove: (entityName, id) => deleteMockEntity(entityName, id)
};

const entityHandlerOverrides = {
  teachers: {
    list: () => listTeachers(),
    create: (_, payload) => createTeacher(payload),
    update: (_, id, payload) => updateTeacher(id, payload),
    remove: (_, id) => deleteTeacher(id)
  }
};

function resolveEntityHandler(entityName) {
  const override = entityHandlerOverrides[entityName];
  if (!override) {
    return defaultEntityHandler;
  }

  return {
    ...defaultEntityHandler,
    ...override
  };
}

// SECTION: Entity API Facade
export async function listEntities(entityName) {
  const handler = resolveEntityHandler(entityName);
  return handler.list(entityName);
}

export async function createEntity(entityName, payload) {
  const handler = resolveEntityHandler(entityName);
  return handler.create(entityName, payload);
}

export async function updateEntity(entityName, id, payload) {
  const handler = resolveEntityHandler(entityName);
  return handler.update(entityName, id, payload);
}

export async function deleteEntity(entityName, id) {
  const handler = resolveEntityHandler(entityName);
  return handler.remove(entityName, id);
}

// SECTION: Timetable API Facade
export async function generateTimetables(payload) {
  return generateMockTimetables(payload);
}

export async function listTimetableGroups() {
  return listMockTimetableGroups();
}

export async function listTimetableEntries(groupId) {
  return listMockTimetableEntries(groupId);
}

export async function updateTimetableEntry(groupId, entryId, payload) {
  return updateMockTimetableEntry(groupId, entryId, payload);
}

export async function swapTimetableEntries(groupId, entryIdA, entryIdB) {
  return swapMockTimetableEntries(groupId, entryIdA, entryIdB);
}
