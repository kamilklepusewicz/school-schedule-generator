// SECTION: Mock In-Memory Database
export const db = {
  teachers: [
    { id: 'T-001', firstName: 'Anna', lastName: 'Kowalska' },
    { id: 'T-002', firstName: 'Piotr', lastName: 'Nowak' },
    { id: 'T-003', firstName: 'Marta', lastName: 'Zielinska' }
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
      start_time: '2026-03-23T08:00',
      end_time: '2026-03-23T08:45'
    },
    {
      id: 'C-0002',
      subject_id: 'S-ENG',
      teacher_id: 'T-002',
      group_id: 'G-1A',
      room_id: 'R-204',
      start_time: '2026-03-23T09:00',
      end_time: '2026-03-23T09:45'
    },
    {
      id: 'C-0003',
      subject_id: 'S-BIO',
      teacher_id: 'T-003',
      group_id: 'G-1B',
      room_id: 'R-302',
      start_time: '2026-03-23T10:00',
      end_time: '2026-03-23T10:45'
    },
    {
      id: 'C-0004',
      subject_id: 'S-MATH',
      teacher_id: 'T-001',
      group_id: 'G-1B',
      room_id: 'R-101',
      start_time: '2026-03-24T08:00',
      end_time: '2026-03-24T08:45'
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