<template>
  <section class="space-y-4 max-w-sm mx-auto">
    <h2 class="text-lg font-semibold text-center">Admin Login</h2>
    <form class="rounded-2xl border bg-white p-4 shadow-sm space-y-3" @submit.prevent="submit">
      <input v-model="token" type="password" class="border rounded-xl px-3 py-2 w-full" placeholder="Enter admin token" />
      <button class="rounded-xl border px-3 py-2 w-full hover:bg-slate-50">Sign In</button>
      <div class="text-xs text-red-600" v-if="err">{{ err }}</div>
      <div class="text-xs text-slate-500" v-if="ok">Signed in.</div>
    </form>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { setToken } from "../api";

const router = useRouter();
const token = ref("");
const err = ref("");
const ok = ref(false);

async function submit(){
  err.value = ""; ok.value = false;
  if (!token.value) { err.value = "Token required"; return; }
  setToken(token.value);
  ok.value = true;
  window.dispatchEvent(new CustomEvent('auth-changed'));
  router.push('/');
}
</script>
