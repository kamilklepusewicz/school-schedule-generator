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
  classGroups: ['/class_groups', '/class-groups', '/student-groups', '/student_groups', '/groups'],
  classRooms: ['/class_rooms', '/class-rooms', '/classrooms', '/classroom', '/rooms'],
  subjects: ['/subjects', '/subject'],
  classes: ['/classes', '/lesson', '/lessons']
};
const resolvedEntityEndpoints = new Map();

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
    first_name: teacher.first_name,
    last_name: teacher.last_name,
    subject_id: teacher.subject_id
  };
}

function toApiTeacher(teacher) {
  return {
    first_name: teacher.first_name,
    last_name: teacher.last_name,
    subject_id: Number(teacher.subject_id)
  };
}

function fromApiClassGroup(group) {
  return {
    id: group.id,
    name: group.name
  };
}

function fromApiClassRoom(room) {
  return {
    id: room.id,
    name: room.name
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
    classgroup_id: classEntry.classgroup_id ?? classEntry.group_id,
    classroom_id: classEntry.classroom_id ?? classEntry.room_id,
    start_date: classEntry.start_date ?? classEntry.start_time,
    end_date: classEntry.end_date ?? classEntry.end_time,
    description: classEntry.description ?? '',
    status: classEntry.status ?? ''
  };
}

function toApiClassGroup(group) {
  return [
    {
      name: group.name
    }
  ];
}

function toApiClassRoom(room) {
  return [
    {
      name: room.name
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
      classgroup_id: Number(classEntry.classgroup_id),
      classroom_id: Number(classEntry.classroom_id),
      start_date: classEntry.start_date,
      end_date: classEntry.end_date,
      description: classEntry.description
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

  return normalized;
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

// SECTION: Entity Handler Registry
const defaultEntityHandler = {
  list: () => Promise.reject(new Error('No entity handler configured.')),
  create: () => Promise.reject(new Error('No entity handler configured.'))
};

const entityHandlerOverrides = {
  teachers: {
    list: () => listEntityFromBackend('teachers'),
    create: (_, payload) => createEntityInBackend('teachers', payload)
  },
  classGroups: {
    list: () => listEntityFromBackend('classGroups'),
    create: (_, payload) => createEntityInBackend('classGroups', payload)
  },
  classRooms: {
    list: () => listEntityFromBackend('classRooms'),
    create: (_, payload) => createEntityInBackend('classRooms', payload)
  },
  subjects: {
    list: () => listEntityFromBackend('subjects'),
    create: (_, payload) => createEntityInBackend('subjects', payload)
  },
  classes: {
    list: () => listEntityFromBackend('classes'),
    create: (_, payload) => createEntityInBackend('classes', payload)
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
