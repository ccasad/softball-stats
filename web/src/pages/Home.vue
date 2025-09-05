<template>
  <section class="space-y-3">
    <div class="rounded-2xl border bg-white p-4 shadow-sm">
      <img :src="logoUrl" alt="Logo" width="250" class="mx-auto mb-2">
    </div>
    <div class="grid grid-cols-3 gap-3">
      <RouterLink to="/players" class="rounded-2xl border bg-white p-4 shadow-sm text-center">Players</RouterLink>
      <RouterLink to="/games" class="rounded-2xl border bg-white p-4 shadow-sm text-center">Games</RouterLink>
      <RouterLink to="/stats" class="rounded-2xl border bg-white p-4 shadow-sm text-center">Stats</RouterLink>
    </div>
  </section>
</template>

<script setup lang="ts">
const logoUrl = import.meta.env.VITE_TEAM_LOGO_URL || "";
</script>