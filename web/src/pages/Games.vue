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

    <div class="rounded-2xl border bg-white shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm min-w-[800px]">
          <thead>
            <tr class="border-b bg-slate-50">
              <th class="text-left py-3 px-4 cursor-pointer hover:bg-slate-100" @click="sortBy('date')">
                Date
                <span v-if="sortField === 'date'" class="ml-1">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="text-left py-3 px-4 cursor-pointer hover:bg-slate-100" @click="sortBy('opponent')">
                Opponent
                <span v-if="sortField === 'opponent'" class="ml-1">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="text-center py-3 px-4 cursor-pointer hover:bg-slate-50" @click="sortBy('location')">
                Location
                <span v-if="sortField === 'location'" class="ml-1">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="text-center py-3 px-4 cursor-pointer hover:bg-slate-50" @click="sortBy('time')">
                Time
                <span v-if="sortField === 'time'" class="ml-1">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="text-center py-3 px-4 cursor-pointer hover:bg-slate-50" @click="sortBy('score_ours')">
                Score
                <span v-if="sortField === 'score_ours'" class="ml-1">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="g in sortedGames" :key="g.id" class="border-b hover:bg-slate-50">
              <td class="py-3 px-4">
                <RouterLink class="font-medium hover:underline" :to="`/games/${g.id}`">
                  {{ g.date }}
                </RouterLink>
              </td>
              <td class="py-3 px-4">
                <RouterLink class="font-medium hover:underline" :to="`/games/${g.id}`">
                  {{ g.opponent }}
                </RouterLink>
              </td>
              <td class="text-center py-3 px-4">{{ g.location || '—' }}</td>
              <td class="text-center py-3 px-4">{{ g.time || '—' }}</td>
              <td class="text-center py-3 px-4">
                <div v-if="g.score_ours != null && g.score_opponent != null" 
                     :class="{'font-semibold text-green-600': g.score_ours > g.score_opponent, 'font-semibold text-red-600': g.score_ours < g.score_opponent}">
                  {{ g.score_ours }} - {{ g.score_opponent }}
                </div>
                <div v-else class="text-slate-400">—</div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="!loading && !err && games.length === 0" class="p-4 text-sm text-slate-500">
      No results yet.
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { listGamesQ, createGame, type Game } from "../api";
import { isAuthed } from "../api";

const authed = ref(isAuthed());
const games = ref<Game[]>([]);
const opponent = ref(""); const date = ref(""); const time = ref(""); const location = ref("");
const qOpponent = ref(""); const dateFrom = ref(""); const dateTo = ref("");
const loading = ref(false); const err = ref("");
const showAdd = ref(false);

// Sorting state
const sortField = ref<'date' | 'opponent' | 'location' | 'time' | 'score_ours'>('date');
const sortDirection = ref<'asc' | 'desc'>('desc'); // Default to newest first

// Computed property for sorted games
const sortedGames = computed(() => {
  const sorted = [...games.value];
  
  sorted.sort((a, b) => {
    let aVal: any, bVal: any;
    
    if (sortField.value === 'date') {
      aVal = new Date(a.date);
      bVal = new Date(b.date);
    } else if (sortField.value === 'score_ours') {
      // For score sorting, use our score as primary, opponent as secondary
      aVal = a.score_ours ?? 0;
      bVal = b.score_ours ?? 0;
    } else {
      aVal = a[sortField.value] || '';
      bVal = b[sortField.value] || '';
    }
    
    if (aVal < bVal) return sortDirection.value === 'asc' ? -1 : 1;
    if (aVal > bVal) return sortDirection.value === 'asc' ? 1 : -1;
    return 0;
  });
  
  return sorted;
});

// Sorting function
function sortBy(field: typeof sortField.value) {
  if (sortField.value === field) {
    // Toggle direction if same field
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    // New field, default to ascending
    sortField.value = field;
    sortDirection.value = 'asc';
  }
}

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

