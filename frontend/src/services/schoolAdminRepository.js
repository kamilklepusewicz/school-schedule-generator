// SECTION: Imports
import {
  generateMockTimetables,
  listMockTimetableEntries,
  listMockTimetableGroups,
  swapMockTimetableEntries,
  updateMockTimetableEntry
} from './mocks/schoolAdminMockRepository';

// SECTION: Runtime Configuration and Local Cache
const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');
const backendEntities = ['teachers', 'classGroups', 'classRooms', 'subjects', 'classes'];
const entityEndpointCandidates = {
  teachers: ['/teachers', '/teacher'],
  classGroups: ['/class-groups', '/class_groups', '/student-groups', '/student_groups', '/groups'],
  classRooms: ['/class-rooms', '/class_rooms', '/classrooms', '/classroom', '/rooms'],
  subjects: ['/subjects', '/subject'],
  classes: ['/classes', '/lesson', '/lessons']
};
const resolvedEntityEndpoints = new Map();
const localEntityOverrides = new Map(
  backendEntities.map((entityName) => [entityName, new Map()])
);
const locallyDeletedEntityIds = new Map(
  backendEntities.map((entityName) => [entityName, new Set()])
);
const ENTITY_LOCAL_CHANGES_STORAGE_KEY = 'schoolAdmin.entityLocalChanges';

// SECTION: Browser Storage Utilities
function canUseStorage() {
  return typeof window !== 'undefined' && Boolean(window.localStorage);
}

function loadEntityLocalChanges() {
  if (!canUseStorage()) {
    return;
  }

  try {
    const raw = window.localStorage.getItem(ENTITY_LOCAL_CHANGES_STORAGE_KEY);
    if (!raw) {
      return;
    }

    const parsed = JSON.parse(raw);

    backendEntities.forEach((entityName) => {
      const entityOverrides = parsed?.overrides?.[entityName] || {};
      const entityDeletions = parsed?.deletions?.[entityName] || [];

      Object.entries(entityOverrides).forEach(([id, entity]) => {
        localEntityOverrides.get(entityName).set(id, entity);
      });

      entityDeletions.forEach((id) => {
        locallyDeletedEntityIds.get(entityName).add(String(id));
      });
    });
  } catch {
    backendEntities.forEach((entityName) => {
      localEntityOverrides.get(entityName).clear();
      locallyDeletedEntityIds.get(entityName).clear();
    });
  }
}

function persistEntityLocalChanges() {
  if (!canUseStorage()) {
    return;
  }

  const serializedOverrides = {};
  const serializedDeletions = {};

  backendEntities.forEach((entityName) => {
    serializedOverrides[entityName] = Object.fromEntries(localEntityOverrides.get(entityName).entries());
    serializedDeletions[entityName] = Array.from(locallyDeletedEntityIds.get(entityName));
  });

  window.localStorage.setItem(
    ENTITY_LOCAL_CHANGES_STORAGE_KEY,
    JSON.stringify({
      overrides: serializedOverrides,
      deletions: serializedDeletions
    })
  );
}

loadEntityLocalChanges();

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

    const error = new Error(message);
    error.status = response.status;
    throw error;
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

function fromApiClassGroup(group) {
  return {
    id: group.id,
    name: group.name,
    no_students: group.no_students ?? group.student_count ?? group.students_count ?? 0
  };
}

function fromApiClassRoom(room) {
  return {
    id: room.id,
    number: room.number,
    name: room.name,
    no_seats: room.no_seats ?? room.seats_count ?? 0
  };
}

function fromApiSubject(subject) {
  return {
    id: subject.id,
    name: subject.name
  };
}

function fromApiClass(classEntry) {
  return {
    id: classEntry.id,
    subject_id: classEntry.subject_id,
    teacher_id: classEntry.teacher_id,
    group_id: classEntry.group_id,
    room_id: classEntry.room_id ?? classEntry.classroom_id,
    start_date: classEntry.start_date ?? classEntry.start_time,
    end_date: classEntry.end_date ?? classEntry.end_time
  };
}

function toApiClassGroup(group) {
  const studentCount = Number(group.no_students);
  return [
    {
      name: group.name,
      no_students: studentCount
    },
    {
      name: group.name,
      student_count: studentCount
    }
  ];
}

function toApiClassRoom(room) {
  const seatsCount = Number(room.no_seats);
  return [
    {
      number: room.number,
      name: room.name,
      no_seats: seatsCount
    },
    {
      number: room.number,
      name: room.name,
      seats_count: seatsCount
    }
  ];
}

function toApiSubject(subject) {
  return [
    {
      name: subject.name
    }
  ];
}

function toApiClass(classEntry) {
  return [
    {
      subject_id: Number(classEntry.subject_id),
      teacher_id: Number(classEntry.teacher_id),
      group_id: Number(classEntry.group_id),
      room_id: Number(classEntry.room_id),
      start_date: classEntry.start_date,
      end_date: classEntry.end_date
    },
    {
      subject_id: Number(classEntry.subject_id),
      teacher_id: Number(classEntry.teacher_id),
      group_id: Number(classEntry.group_id),
      classroom_id: Number(classEntry.room_id),
      start_date: classEntry.start_date,
      end_date: classEntry.end_date
    },
    {
      subject_id: Number(classEntry.subject_id),
      teacher_id: Number(classEntry.teacher_id),
      group_id: Number(classEntry.group_id),
      classroom_id: Number(classEntry.room_id),
      start_time: classEntry.start_date,
      end_time: classEntry.end_date
    }
  ];
}

const entityApiAdapters = {
  teachers: {
    fromApi: fromApiTeacher,
    toApiCandidates: (payload) => [toApiTeacher(payload)]
  },
  classGroups: {
    fromApi: fromApiClassGroup,
    toApiCandidates: toApiClassGroup
  },
  classRooms: {
    fromApi: fromApiClassRoom,
    toApiCandidates: toApiClassRoom
  },
  subjects: {
    fromApi: fromApiSubject,
    toApiCandidates: toApiSubject
  },
  classes: {
    fromApi: fromApiClass,
    toApiCandidates: toApiClass
  }
};

// SECTION: Generic Data Utilities
function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function normalizeListPayload(payload) {
  if (Array.isArray(payload)) {
    return payload;
  }

  if (Array.isArray(payload?.items)) {
    return payload.items;
  }

  if (Array.isArray(payload?.data)) {
    return payload.data;
  }

  throw new Error('Unexpected list response format from backend API.');
}

async function resolveEntityEndpoint(entityName) {
  if (resolvedEntityEndpoints.has(entityName)) {
    return resolvedEntityEndpoints.get(entityName);
  }

  const candidates = entityEndpointCandidates[entityName] || [];

  for (const endpoint of candidates) {
    try {
      await requestJson(endpoint);
      resolvedEntityEndpoints.set(entityName, endpoint);
      return endpoint;
    } catch (error) {
      if (error?.status === 404) {
        continue;
      }

      throw error;
    }
  }

  throw new Error(`No backend endpoint found for "${entityName}".`);
}

function applyEntityLocalChanges(entityName, entities) {
  const deletedIds = locallyDeletedEntityIds.get(entityName);
  const overrides = localEntityOverrides.get(entityName);

  return entities
    .filter((entity) => !deletedIds.has(String(entity.id)))
    .map((entity) => {
      const override = overrides.get(String(entity.id));
      return override
        ? {
          ...entity,
          ...override
        }
        : entity;
    });
}

function clearEntityLocalChanges(entityName, id) {
  const entityId = String(id);
  localEntityOverrides.get(entityName).delete(entityId);
  locallyDeletedEntityIds.get(entityName).delete(entityId);
  persistEntityLocalChanges();
}

async function listEntityFromBackend(entityName) {
  const endpoint = await resolveEntityEndpoint(entityName);
  const payload = await requestJson(endpoint);
  const items = normalizeListPayload(payload);
  const normalized = items.map(entityApiAdapters[entityName].fromApi);

  return applyEntityLocalChanges(entityName, normalized);
}

async function createEntityInBackend(entityName, payload) {
  const endpoint = await resolveEntityEndpoint(entityName);
  const candidates = entityApiAdapters[entityName].toApiCandidates(payload);
  let fallbackError = null;

  for (const candidatePayload of candidates) {
    try {
      const created = await requestJson(endpoint, {
        method: 'POST',
        body: JSON.stringify(candidatePayload)
      });

      const normalized = entityApiAdapters[entityName].fromApi(created);
      clearEntityLocalChanges(entityName, normalized.id);
      return normalized;
    } catch (error) {
      if (error?.status === 422 || error?.status === 400) {
        fallbackError = error;
        continue;
      }

      throw error;
    }
  }

  if (fallbackError) {
    throw fallbackError;
  }

  throw new Error(`Could not create ${entityName}.`);
}

async function updateEntityLocally(entityName, id, payload) {
  const entityId = String(id);
  const existing = (await listEntityFromBackend(entityName))
    .find((entity) => String(entity.id) === entityId);

  if (!existing) {
    throw new Error(`Entry with id "${id}" not found.`);
  }

  const nextEntity = {
    ...existing,
    ...clone(payload)
  };

  localEntityOverrides.get(entityName).set(entityId, nextEntity);
  locallyDeletedEntityIds.get(entityName).delete(entityId);
  persistEntityLocalChanges();
  return clone(nextEntity);
}

async function deleteEntityLocally(entityName, id) {
  const entityId = String(id);
  const existing = (await listEntityFromBackend(entityName))
    .find((entity) => String(entity.id) === entityId);

  if (!existing) {
    throw new Error(`Entry with id "${id}" not found.`);
  }

  locallyDeletedEntityIds.get(entityName).add(entityId);
  localEntityOverrides.get(entityName).delete(entityId);
  persistEntityLocalChanges();
  return existing;
}

// SECTION: Entity Handler Registry
const defaultEntityHandler = {
  list: () => Promise.reject(new Error('No entity handler configured.')),
  create: () => Promise.reject(new Error('No entity handler configured.')),
  update: () => Promise.reject(new Error('No entity handler configured.')),
  remove: () => Promise.reject(new Error('No entity handler configured.'))
};

const entityHandlerOverrides = {
  teachers: {
    list: () => listEntityFromBackend('teachers'),
    create: (_, payload) => createEntityInBackend('teachers', payload),
    update: (_, id, payload) => updateEntityLocally('teachers', id, payload),
    remove: (_, id) => deleteEntityLocally('teachers', id)
  },
  classGroups: {
    list: () => listEntityFromBackend('classGroups'),
    create: (_, payload) => createEntityInBackend('classGroups', payload),
    update: (_, id, payload) => updateEntityLocally('classGroups', id, payload),
    remove: (_, id) => deleteEntityLocally('classGroups', id)
  },
  classRooms: {
    list: () => listEntityFromBackend('classRooms'),
    create: (_, payload) => createEntityInBackend('classRooms', payload),
    update: (_, id, payload) => updateEntityLocally('classRooms', id, payload),
    remove: (_, id) => deleteEntityLocally('classRooms', id)
  },
  subjects: {
    list: () => listEntityFromBackend('subjects'),
    create: (_, payload) => createEntityInBackend('subjects', payload),
    update: (_, id, payload) => updateEntityLocally('subjects', id, payload),
    remove: (_, id) => deleteEntityLocally('subjects', id)
  },
  classes: {
    list: () => listEntityFromBackend('classes'),
    create: (_, payload) => createEntityInBackend('classes', payload),
    update: (_, id, payload) => updateEntityLocally('classes', id, payload),
    remove: (_, id) => deleteEntityLocally('classes', id)
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
