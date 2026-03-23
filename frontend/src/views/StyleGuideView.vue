<template>
  <section class="guide-layout">
    <header class="card">
      <p class="eyebrow">UI Toolkit</p>
      <h1 class="guide-title">Style Guide</h1>
      <p class="muted guide-subtitle">
        Reusable templates and utility classes for forms, tables, navigation, and page structure.
      </p>
    </header>

    <section class="guide-grid">
      <article class="card">
        <h2 class="section-title">Buttons</h2>
        <div class="row">
          <button type="button" class="btn">Default</button>
          <button type="button" class="btn btn-primary">Primary</button>
          <button type="button" class="btn" disabled>Disabled</button>
        </div>
      </article>

      <article class="card">
        <h2 class="section-title">Form Controls</h2>
        <div class="field">
          <label class="label-text" for="guide-subject">Subject</label>
          <input id="guide-subject" class="control" type="text" placeholder="Mathematics" />
        </div>
        <div class="field spaced-field">
          <label class="label-text" for="guide-room">Room</label>
          <input id="guide-room" class="control" type="text" placeholder="B-104" />
        </div>
      </article>

      <article class="card">
        <h2 class="section-title">Cards and Text</h2>
        <p>
          Use <strong>.card</strong> as the default container and <strong>.section-title</strong> for section headings.
          Use the <strong>.muted</strong> utility for supporting descriptions.
        </p>
        <p class="muted">This is muted helper text used for less prominent information.</p>
      </article>

      <article class="card">
        <h2 class="section-title">Table Template</h2>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>Day</th>
                <th>Lesson</th>
                <th>Room</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Monday</td>
                <td>Physics</td>
                <td>A-21</td>
              </tr>
              <tr>
                <td>Tuesday</td>
                <td>History</td>
                <td>C-14</td>
              </tr>
              <tr>
                <td>Wednesday</td>
                <td>Biology</td>
                <td>Lab-2</td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>

      <article class="card full-width">
        <h2 class="section-title">Navigation Link Style</h2>
        <div class="row">
          <span class="sample-link">Dashboard</span>
          <span class="sample-link is-active">Style Guide</span>
          <span class="sample-link is-disabled">Templates</span>
        </div>
      </article>
    </section>
  </section>
</template>

<style scoped>
.guide-layout {
  display: grid;
  gap: 1rem;
}

.eyebrow {
  margin: 0 0 0.3rem;
  color: var(--color-accent-strong);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 0.78rem;
  font-weight: 700;
}

.guide-title {
  margin: 0;
  font-size: clamp(1.4rem, 2vw, 2rem);
}

.guide-subtitle {
  margin: 0.55rem 0 0;
}

.guide-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.55rem;
}

.spaced-field {
  margin-top: 0.85rem;
}

.full-width {
  grid-column: 1 / -1;
}

.sample-link {
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--color-border);
  background: var(--color-surface-2);
  color: var(--color-text-main);
  padding: 0.45rem 0.75rem;
  border-radius: var(--radius-md);
}

.sample-link.is-active {
  border-color: var(--color-accent);
  background: var(--color-accent-soft);
}

.sample-link.is-disabled {
  opacity: 0.65;
}

@media (max-width: 900px) {
  .guide-grid {
    grid-template-columns: 1fr;
  }
}
</style>
