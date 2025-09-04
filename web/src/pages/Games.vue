<template>
  <section class="space-y-4">
    <h2 class="text-lg font-semibold">Games</h2>

    <div v-if="authed" @click="showAdd = !showAdd" class="text-sm text-slate-500 flex justify-end cursor-pointer">Add Game</div>
    <div v-else class="rounded-2xl border bg-white p-4 shadow-sm text-sm text-slate-500">
      <RouterLink class="underline" to="/login">Log in</RouterLink> to add.
    </div>
    <div v-if="authed && showAdd">
      <form class="rounded-2xl border bg-white p-4 shadow-sm grid grid-cols-4 gap-3" @submit.prevent="submit">
        <input v-model="opponent" class="border rounded-xl px-3 py-2 col-span-1" placeholder="Opponent"/>
        <input v-model="date" type="date" class="border rounded-xl px-3 py-2 col-span-1" placeholder="Date"/>
        <input v-model="time" type="text" class="border rounded-xl px-3 py-2 col-span-1" placeholder="Time"/>
        <input v-model="location" class="border rounded-xl px-3 py-2 col-span-1" placeholder="Location"/>
        <button class="rounded-xl border px-3 py-2 hover:bg-slate-50 col-span-1">Add</button>
      </form>
    </div>

    <form class="rounded-2xl border bg-white p-4 shadow-sm grid grid-cols-5 gap-3" @submit.prevent="applyFilters">
      <input v-model="qOpponent" class="border rounded-xl px-3 py-2 col-span-1" placeholder="Opponent" />
      <input v-model="dateFrom" type="date" class="border rounded-xl px-3 py-2 col-span-1" />
      <input v-model="dateTo" type="date" class="border rounded-xl px-3 py-2 col-span-1" />
      <button @click="applyFilters" class="rounded-xl border px-3 py-2 hover:bg-slate-50 col-span-1">Apply</button>
      <button @click="clear" class="rounded-xl border px-3 py-2 hover:bg-slate-50 col-span-1">Clear</button>
    </form>

    <div class="text-sm text-slate-500" v-if="loading">Loading…</div>
    <div class="text-sm text-red-600" v-if="err">{{ err }}</div>

    <div class="rounded-2xl border bg-white p-2 shadow-sm divide-y">
      <div v-for="g in games" :key="g.id" class="flex items-center justify-between p-3">
        <div class="text-sm">
          <RouterLink class="font-medium hover:underline" :to="`/games/${g.id}`">
            {{ g.date }} vs {{ g.opponent }} 
          </RouterLink>
          <div class="text-slate-500">{{ g.location || '—' }}</div>
          <span v-if="g.time" class="text-slate-500">{{ g.time }}</span>
          <div v-if="g.score_ours != null && g.score_opponent != null" class="text-sm" :class="{'font-semibold text-green-600': g.score_ours > g.score_opponent, 'font-semibold text-red-600': g.score_ours < g.score_opponent}">
            {{ g.score_ours }}:{{ g.score_opponent }}
          </div>
        </div>
      </div>
    </div>

    <div v-if="!loading && !err && games.length === 0" class="p-4 text-sm text-slate-500">
      No results yet.
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { listGamesQ, createGame, type Game } from "../api";
import { isAuthed } from "../api";

const authed = ref(isAuthed());
const games = ref<Game[]>([]);
const opponent = ref(""); const date = ref(""); const time = ref(""); const location = ref("");
const qOpponent = ref(""); const dateFrom = ref(""); const dateTo = ref("");
const loading = ref(false); const err = ref("");
const showAdd = ref(false);

async function load() {
  loading.value = true; err.value = "";
  try {
    games.value = await listGamesQ({
      opponent: qOpponent.value || undefined,
      date_from: dateFrom.value || undefined,
      date_to: dateTo.value || undefined
    });
  } catch (e:any) { err.value = e?.message || "Failed to load games"; }
  finally { loading.value = false; }
}
async function clear(){
  qOpponent.value = "";
  dateFrom.value = "";
  dateTo.value = "";
  await load();
}
async function applyFilters(){ await load(); }

async function submit() {
  if (!opponent.value || !date.value) return;
  await createGame({ opponent: opponent.value, date: date.value, time: time.value || undefined, location: location.value || undefined });
  opponent.value = ""; date.value = ""; time.value = ""; location.value = "";
  await load();
}
onMounted(load);
</script>

