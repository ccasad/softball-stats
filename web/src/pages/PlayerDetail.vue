<template>
  <section class="space-y-4">
    <div v-if="!player" class="text-sm text-slate-500">Loading…</div>
    <div v-else class="space-y-3">
      <h2 class="text-lg font-semibold">
        {{ player.first_name }} {{ player.last_name }} <span class="text-slate-500">#{{ player.jersey_number ?? '—' }}</span>
      </h2>

      <div class="rounded-2xl border bg-white p-4 shadow-sm grid grid-cols-3 gap-3">
        <input v-model="dateFrom" type="date" class="border rounded-xl px-3 py-2 col-span-1" />
        <input v-model="dateTo" type="date" class="border rounded-xl px-3 py-2 col-span-1" />
        <button @click="reloadAgg" class="rounded-xl border px-3 py-2 hover:bg-slate-50 col-span-1">Apply Filters</button>
      </div>
      <div class="text-sm text-slate-500" v-if="loading">Loading…</div>
      <div class="text-sm text-red-600" v-if="err">{{ err }}</div>

      <div class="rounded-2xl border bg-white p-4 shadow-sm">
        <h3 class="text-sm font-semibold mb-2">Season Totals</h3>
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
        <div class="px-3 py-2 text-sm font-semibold">Per-Game Lines</div>
        <div class="divide-y">
          <div v-for="row in lines" :key="row.id" class="p-3 text-sm flex flex-wrap gap-x-4">
            <RouterLink class="underline" :to="`/games/${row.game_id}`">Game {{ row.game_id }}</RouterLink>
            <div>AB {{ row.at_bats }}</div>
            <div>H {{ row.hits }}</div>
            <div>1B {{ row.singles }}</div>
            <div>2B {{ row.doubles }}</div>
            <div>3B {{ row.triples }}</div>
            <div>HR {{ row.home_runs }}</div>
            <div>BB {{ row.walks }}</div>
            <div>K {{ row.strikeouts }}</div>
            <div>RBI {{ row.rbis }}</div>
          </div>
        </div>
      </div>

    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { useRoute } from "vue-router";
import { getPlayer, listStats, aggregate, type Player, type Stat } from "../api";

const route = useRoute();
const id = Number(route.params.id);
const player = ref<Player|null>(null);
const lines = ref<Stat[]>([]);
const agg = reactive<any>({at_bats:0,hits:0,total_bases:0,average:0,slugging:0,on_base_percent:0,on_base_percent_plus_slugging:0});

const dateFrom = ref(""); const dateTo = ref("");
const loading = ref(false); const err = ref("");

function fmt(n:number){ return (n ?? 0).toFixed(3); }

async function reloadAgg(){
  loading.value = true; err.value = "";
  try {
    Object.assign(agg, await aggregate({
      player_id: id,
      date_from: dateFrom.value || undefined,
      date_to: dateTo.value || undefined
    }));
  } catch (e:any) { err.value = e?.message || "Failed to load aggregates"; }
  finally { loading.value = false; }
}

async function load(){
  player.value = await getPlayer(id);
  lines.value = await listStats({ player_id: id });
  await reloadAgg();
}

onMounted(load);
</script>

