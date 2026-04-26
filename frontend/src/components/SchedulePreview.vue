<script setup>
defineProps({
  schedule: {
    type: Array,
    default: () => []
  }
});
</script>

<template>
  <section class="card panel">
    <h2 class="section-title">Schedule Preview</h2>

    <p v-if="!schedule.length" class="hint muted">Generate a schedule to see preview.</p>

    <div v-else class="tables">
      <article v-for="day in schedule" :key="day.day" class="day-card">
        <h3>{{ day.day }}</h3>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>Slot</th>
                <th>Subject</th>
                <th>Room</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="lesson in day.lessons" :key="lesson.slot">
                <td>{{ lesson.slot }}</td>
                <td>{{ lesson.subject }}</td>
                <td>{{ lesson.room || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.hint {
  margin: 0;
}

.tables {
  display: grid;
  gap: 0.8rem;
}

.day-card {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 0.75rem;
  background: var(--color-surface-2);
}

.day-card h3 {
  margin: 0 0 0.6rem;
  color: var(--color-accent-strong);
}
</style>
