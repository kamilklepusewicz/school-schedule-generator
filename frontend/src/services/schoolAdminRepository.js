const db = {
  teachers: [
    { id: 'T-001', name: 'Anna Kowalska' },
    { id: 'T-002', name: 'Piotr Nowak' },
    { id: 'T-003', name: 'Marta Zielinska' }
  ],
  classGroups: [
    { id: 'G-1A', name: 'Class 1A', no_students: 28 },
    { id: 'G-1B', name: 'Class 1B', no_students: 25 }
  ],
  classRooms: [
    { id: 'R-101', number: '101', name: 'Math Room', no_seats: 30 },
    { id: 'R-204', number: '204', name: 'Language Lab', no_seats: 26 },
    { id: 'R-302', number: '302', name: 'Science Lab', no_seats: 24 }
  ],
  subjects: [
    { id: 'S-MATH', name: 'Mathematics' },
    { id: 'S-ENG', name: 'English' },
    { id: 'S-BIO', name: 'Biology' }
  ],
  classes: [
    {
      id: 'C-0001',
      subject_id: 'S-MATH',
      teacher_id: 'T-001',
      group_id: 'G-1A',
      room_id: 'R-101',
      start_date: '2026-03-23T08:00',
      end_date: '2026-03-23T08:45'
    },
    {
      id: 'C-0002',
      subject_id: 'S-ENG',
      teacher_id: 'T-002',
      group_id: 'G-1A',
      room_id: 'R-204',
      start_date: '2026-03-23T09:00',
      end_date: '2026-03-23T09:45'
    },
    {
      id: 'C-0003',
      subject_id: 'S-BIO',
      teacher_id: 'T-003',
      group_id: 'G-1B',
      room_id: 'R-302',
      start_date: '2026-03-23T10:00',
      end_date: '2026-03-23T10:45'
    },
    {
      id: 'C-0004',
      subject_id: 'S-MATH',
      teacher_id: 'T-001',
      group_id: 'G-1B',
      room_id: 'R-101',
      start_date: '2026-03-24T08:00',
      end_date: '2026-03-24T08:45'
    }
  ],
  timetableGroups: [
    {
      id: 'TG-0001',
      name: 'Spring Semester - School Wide',
      scope: 'All groups',
      status: 'ready',
      created_at: '2026-03-22T08:30:00.000Z'
    }
  ],
  timetableEntriesByGroup: {
    'TG-0001': [
      {
        id: 'TE-0001',
        subject_id: 'S-MATH',
        teacher_id: 'T-001',
        group_id: 'G-1A',
        room_id: 'R-101',
        day: 'Monday',
        slot: 1
      },
      {
        id: 'TE-0002',
        subject_id: 'S-ENG',
        teacher_id: 'T-002',
        group_id: 'G-1A',
        room_id: 'R-204',
        day: 'Monday',
        slot: 2
      },
      {
        id: 'TE-0003',
        subject_id: 'S-BIO',
        teacher_id: 'T-003',
        group_id: 'G-1B',
        room_id: 'R-302',
        day: 'Tuesday',
        slot: 1
      },
      {
        id: 'TE-0004',
        subject_id: 'S-MATH',
        teacher_id: 'T-001',
        group_id: 'G-1B',
        room_id: 'R-101',
        day: 'Wednesday',
        slot: 3
      }
    ]
  }
};

const entityIdPrefixMap = {
  teachers: 'T',
  classGroups: 'G',
  classRooms: 'R',
  subjects: 'S',
  classes: 'C'
};

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

export async function listEntities(entityName) {
  validateEntityName(entityName);
  return runWithDelay(db[entityName]);
}

export async function createEntity(entityName, payload) {
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

export async function updateEntity(entityName, id, payload) {
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

export async function deleteEntity(entityName, id) {
  validateEntityName(entityName);

  const collection = db[entityName];
  const index = collection.findIndex((entry) => entry.id === id);

  if (index === -1) {
    throw new Error(`Entry with id "${id}" not found.`);
  }

  const [removed] = collection.splice(index, 1);
  return runWithDelay(removed);
}

export async function generateTimetables(payload) {
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

export async function listTimetableGroups() {
  return runWithDelay(db.timetableGroups);
}

export async function listTimetableEntries(groupId) {
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

export async function updateTimetableEntry(groupId, entryId, payload) {
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

export async function swapTimetableEntries(groupId, entryIdA, entryIdB) {
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
