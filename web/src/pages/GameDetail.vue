<template>
  <section class="space-y-4">
    <div v-if="!game" class="text-sm text-slate-500">Loading…</div>
    <div v-else class="space-y-3">
      <h2 class="text-lg font-semibold">{{ game.date }} vs {{ game.opponent }}</h2>
      <div v-if="game.score_ours != null && game.score_opponent != null" class="text-sm text-slate-500" :class="{'font-semibold text-green-600': game.score_ours > game.score_opponent, 'font-semibold text-red-600': game.score_ours < game.score_opponent}">{{ game.score_ours }} - {{ game.score_opponent }}</div>
      <div class="text-sm text-slate-500">{{ game.location }} {{ game.time }}</div>

      <div class="rounded-2xl border bg-white p-2 shadow-sm">
        <div class="px-3 py-2 text-sm font-semibold">Box Score</div>
        <div class="divide-y">
          <div v-for="row in rows" :key="row.id" class="p-3 text-sm flex flex-wrap gap-x-4">
            <RouterLink class="underline" :to="`/players/${row.player_id}`">{{ row.player_first_name }} {{ row.player_last_name }}</RouterLink>
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
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { useRoute } from "vue-router";
import { getGame, listStats, aggregate, type Game, type Stat } from "../api";

const route = useRoute();
const id = Number(route.params.id);
const game = ref<Game|null>(null);
const rows = ref<Stat[]>([]);
const agg = reactive<any>({at_bats:0,hits:0,total_bases:0,average:0,slugging:0,on_base_percent:0,on_base_percent_plus_slugging:0});

function fmt(n:number){ return (n ?? 0).toFixed(3); }

async function load(){
  game.value = await getGame(id);
  rows.value = await listStats({ game_id: id });
  console.log(rows.value);
  Object.assign(agg, await aggregate({ game_id: id }));
}

onMounted(load);
</script>
