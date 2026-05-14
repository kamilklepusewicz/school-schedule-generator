// SECTION: Imports
import {
  generateMockTimetables,
  listMockTimetableEntries,
  listMockTimetableGroups,
  swapMockTimetableEntries,
  updateMockTimetableEntry
} from './mocks/schoolAdminMockRepository';

// SECTION: Runtime Configuration
const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');

// Entity-to-endpoint mapping (matches backend routes)
const entityEndpoints = {
  teachers: '/teachers',
  student_group: '/class_groups',
  classroom: '/class_rooms',
  subjects: '/subjects',
  classes: '/classes',
  classroom_type: '/classroom_types',
  lesson_count: '/lesson_counts'
};

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

// SECTION: Response Normalization (handles field name variations from backend)
const responseNormalizers = {
  teachers: (data) => ({
    id: data.id,
    first_name: data.first_name,
    last_name: data.last_name,
    subject_id: data.subject_id
  }),
  student_group: (data) => ({
    id: data.id,
    name: data.name
  }),
  classroom: (data) => ({
    id: data.id,
    name: data.name,
    classroom_type_id: data.classroom_type_id
  }),
  subjects: (data) => ({
    id: data.id,
    name: data.name,
    classroom_type_id: data.classroom_type_id
  }),
  classes: (data) => ({
    id: data.id,
    subject_id: data.subject_id,
    classroom_id: data.classroom_id ?? data.room_id,
    teacher_id: data.teacher_id,
    group_id: data.group_id ?? data.classgroup_id,
    day: data.day,
    start: data.start,
    description: data.description ?? ''
  }),
  classroom_type: (data) => ({
    id: data.id,
    name: data.name
  }),
  lesson_count: (data) => ({
    id: data.id,
    student_group_id: data.student_group_id,
    subject_id: data.subject_id,
    hours: data.hours
  })
};

// SECTION: Generic Data Utilities
function normalizeListResponse(payload) {
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

async function listEntityFromBackend(entityName) {
  const endpoint = entityEndpoints[entityName];
  if (!endpoint) {
    throw new Error(`Unknown entity: ${entityName}`);
  }

  const response = await requestJson(endpoint);
  const items = normalizeListResponse(response);
  const normalizer = responseNormalizers[entityName];
  
  return items.map((item) => normalizer ? normalizer(item) : item);
}

async function createEntityInBackend(entityName, payload) {
  const endpoint = entityEndpoints[entityName];
  if (!endpoint) {
    throw new Error(`Unknown entity: ${entityName}`);
  }

  // Normalize payload to ensure correct types
  const normalizedPayload = {
    ...payload,
    subject_id: payload.subject_id ? Number(payload.subject_id) : undefined,
    classroom_id: payload.classroom_id ? Number(payload.classroom_id) : undefined,
    teacher_id: payload.teacher_id ? Number(payload.teacher_id) : undefined,
    group_id: payload.group_id ? Number(payload.group_id) : undefined
  };

  // Remove undefined fields
  Object.keys(normalizedPayload).forEach((key) => {
    if (normalizedPayload[key] === undefined) {
      delete normalizedPayload[key];
    }
  });

  const response = await requestJson(endpoint, {
    method: 'POST',
    body: JSON.stringify(normalizedPayload)
  });

  const normalizer = responseNormalizers[entityName];
  return normalizer ? normalizer(response) : response;
}

async function updateEntityInBackend(entityName, entityId, payload) {
  const endpoint = entityEndpoints[entityName];
  if (!endpoint) {
    throw new Error(`Unknown entity: ${entityName}`);
  }

  // Normalize payload to ensure correct types
  const normalizedPayload = {
    ...payload,
    subject_id: payload.subject_id ? Number(payload.subject_id) : undefined,
    classroom_id: payload.classroom_id ? Number(payload.classroom_id) : undefined,
    teacher_id: payload.teacher_id ? Number(payload.teacher_id) : undefined,
    group_id: payload.group_id ? Number(payload.group_id) : undefined,
    classroom_type_id: payload.classroom_type_id ? Number(payload.classroom_type_id) : undefined,
    student_group_id: payload.student_group_id ? Number(payload.student_group_id) : undefined,
    hours: payload.hours ? Number(payload.hours) : undefined,
    day: payload.day ? Number(payload.day) : undefined,
    start: payload.start ? Number(payload.start) : undefined
  };

  // Remove undefined fields
  Object.keys(normalizedPayload).forEach((key) => {
    if (normalizedPayload[key] === undefined) {
      delete normalizedPayload[key];
    }
  });

  const response = await requestJson(`${endpoint}/${entityId}`, {
    method: 'PUT',
    body: JSON.stringify(normalizedPayload)
  });

  const normalizer = responseNormalizers[entityName];
  return normalizer ? normalizer(response) : response;
}

async function deleteEntityInBackend(entityName, entityId) {
  const endpoint = entityEndpoints[entityName];
  if (!endpoint) {
    throw new Error(`Unknown entity: ${entityName}`);
  }

  await requestJson(`${endpoint}/${entityId}`, {
    method: 'DELETE'
  });

  return { id: entityId };
}

// SECTION: Entity API Facade (direct exports)
export async function listEntities(entityName) {
  return listEntityFromBackend(entityName);
}

export async function createEntity(entityName, payload) {
  return createEntityInBackend(entityName, payload);
}

export async function updateEntity(entityName, entityId, payload) {
  return updateEntityInBackend(entityName, entityId, payload);
}

export async function deleteEntity(entityName, entityId) {
  return deleteEntityInBackend(entityName, entityId);
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
