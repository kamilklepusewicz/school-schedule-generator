# Design Architecture and UI Guidelines

This document defines the architecture for the institutional timetable administration app.

## Product Scope

Frontend supports two core administrator workflows:
- Master data management (teachers, class groups, rooms, subjects, classes)
- Timetable generation request submission for all groups or selected groups
- Timetable management for previously generated timetable groups, including manual move and swap edits

The backend owns all scheduling logic and persistence. Frontend focuses on:
- Form-based CRUD interfaces
- Entity tables with tabbed navigation
- Clear operational dashboard and request submission UX

## Design Token System

Primary token source:
- src/assets/base.css

The root token block in :root contains:
- Font variables: --font-family-base
- Surface/background colors: --color-page-start, --color-page-end, --color-surface, --color-surface-2
- Text colors: --color-text-main, --color-text-muted
- Border colors: --color-border, --color-border-strong
- Accent palette: --color-accent, --color-accent-soft, --color-accent-strong
- State colors: --color-danger
- Shape and depth: --radius-sm, --radius-md, --radius-lg, --shadow-soft

Rule:
- Always prefer tokens over hardcoded values.

## Reusable UI Utilities

Defined in src/assets/base.css:
- .card: Standard panel shell
- .section-title: Section heading
- .label-text: Label typography
- .field: Form field layout
- .control: Input/select styling
- .btn: Generic button style
- .btn-primary: Primary action button
- .btn-block: Full-width button helper
- .muted: Secondary text
- .table-wrap: Overflow-safe table wrapper
- .table: Table baseline styling

Rule:
- Add reusable patterns to base.css before writing repeated local styles.

## Application Structure

### Layout Components

- src/components/AppNavbar.vue
- src/components/AppPageHeader.vue
- src/components/AppFooter.vue

### Feature Components

- src/components/admin/EntityCrudPanel.vue: Generic CRUD form + table panel for one entity

### Views

- src/views/HomeView.vue: Operational dashboard with quick access and data summary
- src/views/AdminDataView.vue: Tabbed entity management workspace
- src/views/TimetableGenerationView.vue: Timetable generation request page
- src/views/TimetableManagementView.vue: Manage previously generated timetable groups and fine-tune classes
- src/views/StyleGuideView.vue: Reusable visual reference

### Routing

Defined in src/router/index.js:
- /
- /admin-data
- /timetable-generation
- /timetable-management
- /style-guide

## Data Access Architecture

The data layer is abstracted to simplify future API integration.

Current adapter:
- src/services/schoolAdminRepository.js

State orchestration composable:
- src/composables/useSchoolAdminData.js

Guidelines:
- Views and components call composable methods, not repository directly.
- Repository function names should remain stable when replacing mock logic with real HTTP calls.
- User-facing UI should present human-readable names, not backend/internal IDs.
- Keep payload shapes aligned with backend DTOs:
	- teachers(id, name)
	- classGroups(id, name, no_students)
	- classRooms(id, number, name, no_seats)
	- subjects(id, name)
	- classes(id, subject_id, teacher_id, group_id, room_id, start_date, end_date)

## UX and Interaction Rules

- Each entity is managed in a separate tab.
- Each tab contains:
	- form for add/update
	- table for current records
	- delete action in-row
- Display concise operation feedback after CRUD actions.
- Keep important actions above the fold on desktop.

## Accessibility and Responsiveness

- All form inputs require visible labels.
- Keep adequate color contrast for text and controls.
- Ensure layouts collapse to one column below 900px.
- Keep all data tables horizontally scrollable using .table-wrap.

## Guidelines for Future Changes

When adding features:
1. Reuse existing utilities and layout templates.
2. Extend the repository API surface first if new backend operations are needed.
3. Expose new operations via useSchoolAdminData composable.
4. Keep view components presentation-focused and lightweight.
5. Update Style Guide if new reusable UI patterns are introduced.
6. Update this document when architecture or conventions change.

## Checklist Before Finalizing UI Work

- Token-based colors and spacing used.
- Reusable classes used for cards/forms/buttons/tables.
- New pages registered in router and linked in navbar when user-facing.
- CRUD and generation flows wired through composable methods.
- Mobile layouts verified.
- No editor/lint errors introduced.
