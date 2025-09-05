<template>
  <div class="min-h-screen">
    <header class="sticky top-0 z-10 bg-white/80 backdrop-blur border-b">
      <div class="mx-auto max-w-3xl px-4 py-3 flex items-center justify-between">
        <h1 class="text-lg font-bold">{{teamName}}</h1>
        <nav class="text-sm flex gap-5">
          <RouterLink 
          class=" hover:underline" 
            :class="{ 'underline': isActiveRoute('/') }"
            to="/"
          >
            Home
          </RouterLink>
          <RouterLink 
          class=" hover:underline" 
            :class="{ 'underline': isActiveRoute('/players') }"
            to="/players"
          >
            Players
          </RouterLink>
          <RouterLink 
          class=" hover:underline" 
            :class="{ 'underline': isActiveRoute('/games') }"
            to="/games"
          >
            Games
          </RouterLink>
          <RouterLink 
            class=" hover:underline" 
            :class="{ 'underline': isActiveRoute('/stats') }"
            to="/stats"
          >
            Stats
          </RouterLink>
          <RouterLink 
            v-if="!authed"
            class="hover:underline" 
            :class="{ 'underline': isActiveRoute('/login') }"
            to="/login"
          >
            Login
          </RouterLink>
          <button v-if="authed" @click="logout" class="hover:underline">Logout</button>
        </nav>
      </div>
    </header>

    <main class="mx-auto px-4 py-6">
      <RouterView />
    </main>

    <footer class="mx-auto max-w-3xl px-4 py-8 text-center text-xs text-slate-500">
      © {{year}} Chris Casad
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { setToken } from "./api";

const router = useRouter();
const route = useRoute();
const year = new Date().getFullYear();

const token = ref(localStorage.getItem("ADMIN_TOKEN") || "");
const authed = computed(() => !!token.value);

const teamName = import.meta.env.VITE_TEAM_NAME || "Unknown Team";

const isActiveRoute = (path: string) => route.path === path;

function logout(){ 
  setToken("");
  token.value = "";
  router.push('/');
}

function refreshAuth() {
  token.value = localStorage.getItem("ADMIN_TOKEN") || "";
}

function handleAuthChange() {
  refreshAuth();
}

onMounted(() => {
  refreshAuth();
  window.addEventListener('auth-changed', handleAuthChange);
});

onUnmounted(() => {
  window.removeEventListener('auth-changed', handleAuthChange);
});
</script>

