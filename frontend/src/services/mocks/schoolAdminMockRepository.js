// SECTION: Imports
import { db } from './schoolAdminMockDb';

// SECTION: Mock Entity Configuration
const entityIdPrefixMap = {
  teachers: 'T',
  classGroups: 'G',
  classRooms: 'R',
  subjects: 'S',
  classes: 'C'
};

// SECTION: Internal Utility Functions
function nextId(prefix) {
  return `${prefix}-${Math.random().toString(36).slice(2, 8).toUpperCase()}`;
}

function getById(entityName, id) {
  return db[entityName].find((entry) => entry.id === id);
}

function displayName(entityName, id) {
  const entry = getById(entityName, id);
  if (!entry) {
    return '-';
  }

  if (entityName === 'teachers') {
    return `${entry.firstName || ''} ${entry.lastName || ''}`.trim();
  }

  if (entityName === 'classRooms') {
    return `${entry.number} ${entry.name}`;
  }

  return entry.name;
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function validateEntityName(entityName) {
  if (!Object.prototype.hasOwnProperty.call(db, entityName)) {
    throw new Error(`Unknown entity: ${entityName}`);
  }
}

function runWithDelay(payload) {
  return new Promise((resolve) => {
    setTimeout(() => resolve(clone(payload)), 120);
  });
}

// SECTION: Mock Entity CRUD Operations
export async function listMockEntities(entityName) {
  validateEntityName(entityName);
  return runWithDelay(db[entityName]);
}

export async function createMockEntity(entityName, payload) {
  validateEntityName(entityName);

  const collection = db[entityName];
  const nextPayload = {
    ...clone(payload),
    id: payload.id || nextId(entityIdPrefixMap[entityName] || 'E')
  };

  const duplicate = collection.some((entry) => entry.id === nextPayload.id);

  if (duplicate) {
    throw new Error('Entry already exists.');
  }

  collection.push(clone(nextPayload));
  return runWithDelay(nextPayload);
}

export async function updateMockEntity(entityName, id, payload) {
  validateEntityName(entityName);

  const collection = db[entityName];
  const index = collection.findIndex((entry) => entry.id === id);

  if (index === -1) {
    throw new Error(`Entry with id "${id}" not found.`);
  }

  collection[index] = {
    ...collection[index],
    ...clone(payload)
  };

  return runWithDelay(collection[index]);
}

export async function deleteMockEntity(entityName, id) {
  validateEntityName(entityName);

  const collection = db[entityName];
  const index = collection.findIndex((entry) => entry.id === id);

  if (index === -1) {
    throw new Error(`Entry with id "${id}" not found.`);
  }

  const [removed] = collection.splice(index, 1);
  return runWithDelay(removed);
}

// SECTION: Mock Timetable Operations
export async function generateMockTimetables(payload) {
  const groupId = nextId('TG');
  const targetGroups = payload.target_group_id === 'all'
    ? db.classGroups
    : db.classGroups.filter((group) => group.id === payload.target_group_id);

  const createdGroup = {
    id: groupId,
    name: payload.name || `Generated ${new Date().toLocaleString()}`,
    scope: payload.target_group_id === 'all'
      ? 'All groups'
      : displayName('classGroups', payload.target_group_id),
    status: 'ready',
    created_at: new Date().toISOString()
  };

  db.timetableGroups.unshift(createdGroup);

  const classPool = db.classes.filter((entry) => targetGroups.some((group) => group.id === entry.group_id));

  db.timetableEntriesByGroup[groupId] = classPool.map((entry, index) => ({
    id: nextId('TE'),
    subject_id: entry.subject_id,
    teacher_id: entry.teacher_id,
    group_id: entry.group_id,
    room_id: entry.room_id,
    day: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'][index % 5],
    slot: (index % 7) + 1
  }));

  const response = {
    request_id: `REQ-${Date.now()}`,
    status: 'queued',
    created_at: new Date().toISOString(),
    generated_group_id: groupId,
    generated_group_name: createdGroup.name,
    target_group_name: createdGroup.scope,
    ...payload
  };

  return runWithDelay(response);
}

export async function listMockTimetableGroups() {
  return runWithDelay(db.timetableGroups);
}

export async function listMockTimetableEntries(groupId) {
  const entries = db.timetableEntriesByGroup[groupId] || [];

  return runWithDelay(
    entries.map((entry) => ({
      ...entry,
      subject_name: displayName('subjects', entry.subject_id),
      teacher_name: displayName('teachers', entry.teacher_id),
      group_name: displayName('classGroups', entry.group_id),
      room_name: displayName('classRooms', entry.room_id)
    }))
  );
}

export async function updateMockTimetableEntry(groupId, entryId, payload) {
  const entries = db.timetableEntriesByGroup[groupId] || [];
  const index = entries.findIndex((entry) => entry.id === entryId);

  if (index === -1) {
    throw new Error('Timetable entry not found.');
  }

  entries[index] = {
    ...entries[index],
    ...clone(payload)
  };

  return runWithDelay(entries[index]);
}

export async function swapMockTimetableEntries(groupId, entryIdA, entryIdB) {
  const entries = db.timetableEntriesByGroup[groupId] || [];
  const entryA = entries.find((entry) => entry.id === entryIdA);
  const entryB = entries.find((entry) => entry.id === entryIdB);

  if (!entryA || !entryB) {
    throw new Error('Swap failed. Entry missing.');
  }

  const slotA = { day: entryA.day, slot: entryA.slot };

  entryA.day = entryB.day;
  entryA.slot = entryB.slot;

  entryB.day = slotA.day;
  entryB.slot = slotA.slot;

  return runWithDelay({
    swapped: true,
    first: entryA.id,
    second: entryB.id
  });
}