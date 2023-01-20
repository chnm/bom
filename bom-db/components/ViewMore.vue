<template>
  <!-- this component displays additional data in a modal view when a user selects a row in the table -->
  <div v-if="show" class="modal">
    <div class="modal-background"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">{{ title }}</p>
        <button
          class="delete"
          aria-label="close"
          @click="show = false"
        ></button>
      </header>
      <section class="modal-card-body">
        <slot><!-- Content --></slot>
      </section>
      <footer class="modal-card-foot">
        <button class="button is-success" @click="show = false">Close</button>
      </footer>
    </div>
  </div>
</template>
