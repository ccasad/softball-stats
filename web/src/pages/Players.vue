<template>
  <section class="space-y-4 w-full">
    <h2 class="text-lg font-semibold">Players</h2>

    <!-- <div v-if="authed" @click="showAdd = !showAdd" class="text-sm text-slate-500 flex justify-end cursor-pointer">Add Player</div>
    <div v-else class="rounded-2xl border bg-white p-4 shadow-sm text-sm text-slate-500">
      <RouterLink class="underline" to="/login">Log in</RouterLink> to add.
    </div>
    <form v-if="authed && showAdd" class="rounded-2xl border bg-white p-4 shadow-sm grid grid-cols-4 gap-3" @submit.prevent="submit">
      <input v-model="first" class="border rounded-xl px-3 py-2 col-span-1" placeholder="First name"/>
      <input v-model="last" class="border rounded-xl px-3 py-2 col-span-1" placeholder="Last name"/>
      <input v-model.number="num" type="number" class="border rounded-xl px-3 py-2 col-span-1" placeholder="Jersey #"/>
      <button class="rounded-xl border px-3 py-2 hover:bg-slate-50 col-span-1">Add</button>
    </form> -->
    

    <div class="rounded-2xl border bg-white p-4 shadow-sm grid grid-cols-2 gap-3">
      <input v-model="q" class="border rounded-xl px-3 py-2 col-span-2" placeholder="Search players by name..." @input="debounceLoad()" />
    </div>

    <div class="text-sm text-slate-500" v-if="loading">Loading…</div>
    <div class="text-sm text-red-600" v-if="err">{{ err }}</div>

    <div class="rounded-2xl border bg-white shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm min-w-[1200px] lg:min-w-[1400px] xl:min-w-[1600px]">
          <thead>
            <tr class="border-b bg-slate-50">
              <th class="text-left py-3 px-4 cursor-pointer hover:bg-slate-100" @click="sortBy('name')">
                Player
                <span v-if="sortField === 'name'" class="ml-1">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="text-center py-3 px-4 cursor-pointer hover:bg-slate-50" @click="sortBy('games_played')">
                G
                <span v-if="sortField === 'games_played'" class="ml-1">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="text-center py-3 px-4 cursor-pointer hover:bg-slate-50" @click="sortBy('plate_appearances')">
                PA
                <span v-if="sortField === 'plate_appearances'" class="ml-1">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="text-center py-3 px-4 cursor-pointer hover:bg-slate-50" @click="sortBy('at_bats')">
                AB
                <span v-if="sortField === 'at_bats'" class="ml-1">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="text-center py-3 px-4 cursor-pointer hover:bg-slate-50" @click="sortBy('hits')">
                H
                <span v-if="sortField === 'hits'" class="ml-1">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="text-center py-3 px-4 cursor-pointer hover:bg-slate-50" @click="sortBy('total_bases')">
                TB
                <span v-if="sortField === 'total_bases'" class="ml-1">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="text-center py-3 px-4 cursor-pointer hover:bg-slate-50" @click="sortBy('singles')">
                1B
                <span v-if="sortField === 'singles'" class="ml-1">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="text-center py-3 px-4 cursor-pointer hover:bg-slate-50" @click="sortBy('doubles')">
                2B
                <span v-if="sortField === 'doubles'" class="ml-1">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="text-center py-3 px-4 cursor-pointer hover:bg-slate-50" @click="sortBy('triples')">
                3B
                <span v-if="sortField === 'triples'" class="ml-1">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="text-center py-3 px-4 cursor-pointer hover:bg-slate-50" @click="sortBy('home_runs')">
                HR
                <span v-if="sortField === 'home_runs'" class="ml-1">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="text-center py-3 px-4 cursor-pointer hover:bg-slate-50" @click="sortBy('rbis')">
                RBI
                <span v-if="sortField === 'rbis'" class="ml-1">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="text-center py-3 px-4 cursor-pointer hover:bg-slate-50" @click="sortBy('walks')">
                BB
                <span v-if="sortField === 'walks'" class="ml-1">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="text-center py-3 px-4 cursor-pointer hover:bg-slate-50" @click="sortBy('strikeouts')">
                K
                <span v-if="sortField === 'strikeouts'" class="ml-1">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="text-center py-3 px-4 cursor-pointer hover:bg-slate-50" @click="sortBy('sac_bunts')">
                SB
                <span v-if="sortField === 'sac_bunts'" class="ml-1">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="text-center py-3 px-4 cursor-pointer hover:bg-slate-50" @click="sortBy('sac_flies')">
                SF
                <span v-if="sortField === 'sac_flies'" class="ml-1">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="text-center py-3 px-4 cursor-pointer hover:bg-slate-50" @click="sortBy('hit_by_pitches')">
                HBP
                <span v-if="sortField === 'hit_by_pitches'" class="ml-1">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              
              <th class="text-center py-3 px-4 cursor-pointer hover:bg-slate-50" @click="sortBy('average')">
                AVG
                <span v-if="sortField === 'average'" class="ml-1">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="text-center py-3 px-4 cursor-pointer hover:bg-slate-50" @click="sortBy('slugging')">
                SLG
                <span v-if="sortField === 'slugging'" class="ml-1">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="text-center py-3 px-4 cursor-pointer hover:bg-slate-50" @click="sortBy('on_base_percent')">
                OBP
                <span v-if="sortField === 'on_base_percent'" class="ml-1">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="text-center py-3 px-4 cursor-pointer hover:bg-slate-50" @click="sortBy('on_base_percent_plus_slugging')">
                OPS
                <span v-if="sortField === 'on_base_percent_plus_slugging'" class="ml-1">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>

              <th class="text-center py-3 px-4 cursor-pointer hover:bg-slate-50" @click="sortBy('errors')">
                E
                <span v-if="sortField === 'errors'" class="ml-1">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in sortedPlayers" :key="p.id" class="border-b hover:bg-slate-50">
              <td class="py-3 px-4">
                <RouterLink class="font-medium hover:underline" :to="`/players/${p.id}`">
                  {{ p.first_name }} {{ p.last_name }} <span class="text-xs text-slate-500 ml-3">#{{ p.jersey_number || '—' }}</span>
                </RouterLink>
                
              </td>
              <td class="text-center py-3 px-4" :class="{ 'bg-green-100 font-semibold': isTop3('games_played', p.games_played) }">{{ p.games_played }}</td>
              <td class="text-center py-3 px-4" :class="{ 'bg-green-100 font-semibold': isTop3('plate_appearances', p.plate_appearances) }">{{ p.plate_appearances }}</td>
              <td class="text-center py-3 px-4" :class="{ 'bg-green-100 font-semibold': isTop3('at_bats', p.at_bats) }">{{ p.at_bats }}</td>
              <td class="text-center py-3 px-4" :class="{ 'bg-green-100 font-semibold': isTop3('hits', p.hits) }">{{ p.hits }}</td>
              <td class="text-center py-3 px-4" :class="{ 'bg-green-100 font-semibold': isTop3('total_bases', p.total_bases) }">{{ p.total_bases }}</td>
              <td class="text-center py-3 px-4" :class="{ 'bg-green-100 font-semibold': isTop3('singles', p.singles) }">{{ p.singles }}</td>
              <td class="text-center py-3 px-4" :class="{ 'bg-green-100 font-semibold': isTop3('doubles', p.doubles) }">{{ p.doubles }}</td>
              <td class="text-center py-3 px-4" :class="{ 'bg-green-100 font-semibold': isTop3('triples', p.triples) }">{{ p.triples }}</td>
              <td class="text-center py-3 px-4" :class="{ 'bg-green-100 font-semibold': isTop3('home_runs', p.home_runs) }">{{ p.home_runs }}</td>
              <td class="text-center py-3 px-4" :class="{ 'bg-green-100 font-semibold': isTop3('rbis', p.rbis) }">{{ p.rbis }}</td>
              <td class="text-center py-3 px-4" :class="{ 'bg-green-100 font-semibold': isTop3('walks', p.walks) }">{{ p.walks }}</td>
              <td class="text-center py-3 px-4" :class="{ 'bg-green-100 font-semibold': isTop3('strikeouts', p.strikeouts) }">{{ p.strikeouts }}</td>
              <td class="text-center py-3 px-4" :class="{ 'bg-green-100 font-semibold': isTop3('sac_bunts', p.sac_bunts) }">{{ p.sac_bunts }}</td>
              <td class="text-center py-3 px-4" :class="{ 'bg-green-100 font-semibold': isTop3('sac_flies', p.sac_flies) }">{{ p.sac_flies }}</td>
              <td class="text-center py-3 px-4" :class="{ 'bg-green-100 font-semibold': isTop3('hit_by_pitches', p.hit_by_pitches) }">{{ p.hit_by_pitches }}</td>
              
              <td class="text-center py-3 px-4" :class="{ 'bg-green-100 font-semibold': isTop3('average', p.average) }">{{ p.average.toFixed(3) }}</td>
              <td class="text-center py-3 px-4" :class="{ 'bg-green-100 font-semibold': isTop3('slugging', p.slugging) }">{{ p.slugging.toFixed(3) }}</td>
              <td class="text-center py-3 px-4" :class="{ 'bg-green-100 font-semibold': isTop3('on_base_percent', p.on_base_percent) }">{{ p.on_base_percent.toFixed(3) }}</td>
              <td class="text-center py-3 px-4" :class="{ 'bg-green-100 font-semibold': isTop3('on_base_percent_plus_slugging', p.on_base_percent_plus_slugging) }">{{ p.on_base_percent_plus_slugging.toFixed(3) }}</td>

              <td class="text-center py-3 px-4" :class="{ 'bg-green-100 font-semibold': isTop3('errors', p.errors) }">{{ p.errors }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="!loading && !err && players.length === 0" class="p-4 text-sm text-slate-500">
      No results yet.
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { listPlayersQ, createPlayer, type Player } from "../api";
import { isAuthed } from "../api";

const authed = ref(isAuthed());
const players = ref<Player[]>([]);
const first = ref(""); const last = ref(""); const num = ref<number | null>(null);
const q = ref("");
const loading = ref(false);
const err = ref("");
const showAdd = ref(false);

const sortField = ref<'name' | 'games_played' | 'plate_appearances' | 'at_bats' | 'hits' | 'total_bases' | 'average' | 'slugging' | 'on_base_percent' | 'on_base_percent_plus_slugging' | 'singles' | 'doubles' | 'triples' | 'home_runs' | 'rbis' | 'walks' | 'strikeouts' | 'sac_bunts' | 'sac_flies' | 'hit_by_pitches' | 'errors'>('name');
const sortDirection = ref<'asc' | 'desc'>('asc');

async function load() {
  loading.value = true; err.value = "";
  try {
    players.value = await listPlayersQ({ q: q.value || undefined });
  } catch (e:any) {
    err.value = e?.message || "Failed to load players";
  } finally {
    loading.value = false;
  }
}
let t:any; function debounceLoad(){ clearTimeout(t); t = setTimeout(load, 300); }

async function submit() {
  if (!first.value || !last.value) return;
  await createPlayer({ first_name: first.value, last_name: last.value, jersey_number: num.value ?? null });
  first.value = ""; last.value = ""; num.value = null;
  await load();
}

// Computed property to get top 3 values for each stat
const topStats = computed(() => {
  const stats = ['hits', 'total_bases', 'average', 'slugging', 'on_base_percent', 'on_base_percent_plus_slugging', 'singles', 'doubles', 'triples', 'home_runs', 'rbis', 'walks', 'strikeouts', 'sac_bunts', 'sac_flies', 'hit_by_pitches', 'errors'];
  const topValues: Record<string, number[]> = {};
  
  stats.forEach(stat => {
    const values = players.value.map(p => p[stat as keyof typeof players.value[0]] as number);
    
    if (stat === 'errors') {
      // For errors, sort ascending (lowest first) and take top 3
      const sortedValues = [...values].sort((a, b) => a - b);
      const top3 = sortedValues.slice(0, 3);
      topValues[stat] = top3;
    } else {
      // For all other stats, sort descending (highest first) and take top 3, excluding 0
      const nonZeroValues = values.filter(v => v > 0);
      const sortedValues = nonZeroValues.sort((a, b) => b - a);
      const top3 = sortedValues.slice(0, 3);
      topValues[stat] = top3;
    }
  });
  
  return topValues;
});

// Function to check if a value is in top 3
function isTop3(stat: string, value: number): boolean {
  return topStats.value[stat]?.includes(value) ?? false;
}

// Computed property for sorted players
const sortedPlayers = computed(() => {
  const sorted = [...players.value];
  
  sorted.sort((a, b) => {
    let aVal: any, bVal: any;
    
    if (sortField.value === 'name') {
      aVal = `${a.first_name} ${a.last_name}`;
      bVal = `${b.first_name} ${b.last_name}`;
    } else {
      aVal = a[sortField.value];
      bVal = b[sortField.value];
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

onMounted(load);
</script>

