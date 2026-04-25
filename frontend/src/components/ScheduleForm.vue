<script setup>
import { reactive } from 'vue';

const emit = defineEmits(['generate']);

const state = reactive({
  selectedDays: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
  lessonsPerDay: 6
});

const allDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];

function toggleDay(day) {
  if (state.selectedDays.includes(day)) {
    state.selectedDays = state.selectedDays.filter((d) => d !== day);
    return;
  }
  state.selectedDays = [...state.selectedDays, day];
}

function generateSchedule() {
  if (!state.selectedDays.length) {
    return;
  }

  emit('generate', {
    days: state.selectedDays,
    lessonsPerDay: state.lessonsPerDay
  });
}
</script>

<template>
  <aside class="card panel">
    <h2 class="section-title">Schedule Setup</h2>

    <label class="field">
      <span class="label-text">Lessons per day</span>
      <input v-model.number="state.lessonsPerDay" min="1" max="12" type="number" class="control" />
    </label>

    <p class="label">Days</p>
    <div class="days">
      <button
        v-for="day in allDays"
        :key="day"
        type="button"
        :class="['btn', 'day-btn', { active: state.selectedDays.includes(day) }]"
        @click="toggleDay(day)"
      >
        {{ day }}
      </button>
    </div>

    <button class="btn btn-primary btn-block" type="button" @click="generateSchedule">Generate</button>
  </aside>
</template>

<style scoped>
.field {
  margin-bottom: 1rem;
}

.label {
  margin: 0 0 0.5rem;
  color: var(--color-text-muted);
  font-weight: 600;
}

.days {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-bottom: 1rem;
}

.day-btn.active {
  background: var(--color-accent-soft);
  border-color: var(--color-accent);
  color: var(--color-accent-strong);
}
</style>
