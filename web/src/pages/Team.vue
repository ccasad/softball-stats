<template>
  <section class="space-y-4">
    <h2 class="text-lg font-semibold">Team Season</h2>

    <div class="rounded-2xl border bg-white p-4 shadow-sm grid grid-cols-5 gap-3">
      <input v-model="opponent" class="border rounded-xl px-3 py-2 col-span-1" placeholder="Opponent" />
      <input v-model="dateFrom" type="date" class="border rounded-xl px-3 py-2 col-span-1" />
      <input v-model="dateTo" type="date" class="border rounded-xl px-3 py-2 col-span-1" />
      <button @click="apply" class="rounded-xl border px-3 py-2 hover:bg-slate-50 col-span-1">Apply</button>
      <button @click="clear" class="rounded-xl border px-3 py-2 hover:bg-slate-50 col-span-1">Clear</button>
      <div class="text-sm text-slate-500 col-span-2" v-if="loading">Calculating…</div>
      <div class="text-sm text-red-600 col-span-2" v-if="err">{{ err }}</div>
    </div>

    <div class="rounded-2xl border bg-white p-4 shadow-sm">
      <h3 class="text-sm font-semibold mb-2">Team Totals</h3>
      <div class="grid grid-cols-3 gap-2 text-sm">
        <div>AB: {{ agg.at_bats }}</div>
        <div>H: {{ agg.hits }}</div>
        <div>TB: {{ agg.total_bases }}</div>
        <div>AVG: {{ fmt(agg.average) }}</div>
        <div>OBP: {{ fmt(agg.on_base_percent) }}</div>
        <div>SLG: {{ fmt(agg.slugging) }}</div>
        <div class="col-span-3">OPS: {{ fmt(agg.on_base_percent_plus_slugging) }}</div>
      </div>
    </div>

    <div class="rounded-2xl border bg-white p-2 shadow-sm">
      <div class="px-3 py-2 text-sm font-semibold">Games</div>
      <div class="divide-y">
        <div v-for="g in games" :key="g.id" class="p-3 text-sm flex items-center justify-between">
          <div>
            <RouterLink class="underline" :to="`/games/${g.id}`">{{ g.date }} vs {{ g.opponent }}</RouterLink>
            <div class="text-slate-500 text-xs">{{ g.location || '—' }}</div>
          </div>
          <div class="text-xs text-slate-500">{{ new Date(g.created_at).toLocaleDateString() }}</div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from "vue";
import { listGamesQ, aggregate, type Game } from "../api";

const games = ref<Game[]>([]);
const opponent = ref("");
const dateFrom = ref("");
const dateTo = ref("");
const loading = ref(false);
const err = ref("");
const agg = reactive<any>({at_bats:0,hits:0,total_bases:0,average:0,slugging:0,on_base_percent:0,on_base_percent_plus_slugging:0});
function fmt(n:number){ return (n ?? 0).toFixed(3); }

async function load(){
  loading.value = true; err.value = "";
  try {
    games.value = await listGamesQ({
      opponent: opponent.value || undefined,
      date_from: dateFrom.value || undefined,
      date_to: dateTo.value || undefined
    });
    Object.assign(agg, await aggregate({
      date_from: dateFrom.value || undefined,
      date_to: dateTo.value || undefined
    }));
  } catch (e:any) { err.value = e?.message || "Failed to load team data"; }
  finally { loading.value = false; }
}
async function apply(){ await load(); }
async function clear(){
  opponent.value = "";
  dateFrom.value = "";
  dateTo.value = "";
  await load();
}

onMounted(load);
</script>
