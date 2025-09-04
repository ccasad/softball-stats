<template>
  <section class="space-y-4">
    <h2 class="text-lg font-semibold">Enter New Stats</h2>

    <div class="rounded-2xl border bg-white p-4 shadow-sm space-y-3">
      <div v-if="authed">
        <label class="block text-sm">Player</label>
        <select v-model.number="playerId" class="border rounded-xl px-3 py-2 w-full">
          <option disabled value="">Select player</option>
          <option v-for="p in players" :key="p.id" :value="p.id">{{ p.first_name }} {{ p.last_name }} (#{{p.jersey_number ?? '—'}})</option>
        </select>

        <label class="block text-sm mt-3">Game</label>
        <select v-model.number="gameId" class="border rounded-xl px-3 py-2 w-full">
          <option disabled value="">Select game</option>
          <option v-for="g in games" :key="g.id" :value="g.id">{{ g.date }} vs {{ g.opponent }}</option>
        </select>

        <div class="grid grid-cols-3 gap-2 mt-4">
          <div v-for="f in fields" :key="f" class="flex flex-col">
            <label :for="f" class="block text-sm font-medium text-gray-700 mb-1">
              {{ getLabel(f) }}
            </label>
            <input
              :aria-label="f" type="number" min="0" step="1"
              class="border rounded-xl px-3 py-2"
              :class="{'border-red-500': negatives || (f==='hits' && hitsMismatch) || hitsExceedPA}"
              :placeholder="f"
              v-model.number="form[f]"
              @input="clampNonNeg(f)"
              inputmode="numeric"
              enterkeyhint="done"
            />
            <small v-if="f==='hits' && hitsMismatch" class="text-xs text-red-600">Hits must equal 1B+2B+3B+HR</small>
          </div>
        </div>

        <div class="flex gap-2 mt-3">
          <button :disabled="!canSave" @click="submit" class="rounded-xl border px-3 py-2 flex-1 disabled:opacity-50">
            {{ saving ? 'Saving…' : 'Save Stats' }}
          </button>
          <button @click="clearForm" class="rounded-xl border px-3 py-2 hover:bg-slate-50">
            Clear
          </button>
        </div>
      </div>

      <div v-else class="rounded-2xl border bg-white p-4 shadow-sm text-sm text-slate-500">
        <RouterLink class="underline" to="/login">Log in</RouterLink> to add. 
      </div>

      <div class="text-xs text-red-600 mt-2" v-if="hitsExceedPA">Hits cannot exceed Plate Appearances (AB + BB + HBP + SF)</div>
      <div class="text-xs text-red-600 mt-1" v-if="negatives">All values must be 0 or more</div>
      <div class="text-xs text-slate-500 mt-2" v-if="msg">{{ msg }}</div>

      <Toast ref="toast" />

    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, computed } from "vue";
import { listPlayers, listGames, upsertStat, type Player, type Game } from "../api";
import Toast from "../components/Toast.vue";
import { isAuthed } from "../api";

const authed = ref(isAuthed());
const players = ref<Player[]>([]);
const games = ref<Game[]>([]);
const playerId = ref<number | null>(null);
const gameId = ref<number | null>(null);
const msg = ref("");
const saving = ref(false);
const toast = ref<{ open: (m: string) => void }>();

const fields = [
  "at_bats","hits","singles","doubles","triples","home_runs",
  "rbis","walks","strikeouts","sac_flies","hit_by_pitches","errors"
] as const;

const form = reactive<Record<(typeof fields)[number], number>>({
  at_bats:0,hits:0,singles:0,doubles:0,triples:0,home_runs:0,
  rbis:0,walks:0,strikeouts:0,sac_flies:0,hit_by_pitches:0,errors:0
});

// --- client-side validation helpers ---
const totalHitsBreakdown = computed(() =>
  form.singles + form.doubles + form.triples + form.home_runs
);

const hitsMismatch = computed(() => form.hits !== totalHitsBreakdown.value);
const negatives = computed(() => fields.some(f => form[f] < 0));
const pa = computed(() => form.at_bats + form.walks + form.hit_by_pitches + form.sac_flies);
const hitsExceedPA = computed(() => form.hits > pa.value);

const canSave = computed(() =>
  !!playerId.value &&
  !!gameId.value &&
  !negatives.value &&
  !hitsMismatch.value &&
  !hitsExceedPA.value &&
  !saving.value
);

function getLabel(f:(typeof fields)[number]) {
  return f.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function clampNonNeg(f:(typeof fields)[number]) {
  if (form[f] < 0 || Number.isNaN(form[f])) form[f] = 0;
}

async function submit() {
  msg.value = "";
  if (!canSave.value) { msg.value = "Please fix validation errors."; return; }
  saving.value = true;
  try {
    await upsertStat({ player_id: playerId.value!, game_id: gameId.value!, ...form });
    toast.value?.open("Saved!");
  } catch (e:any) {
    // Surface Pydantic/validation errors from API (422) or generic error
    const apiDetail = e?.response?.data?.detail;
    msg.value = (typeof apiDetail === "string")
      ? apiDetail
      : (Array.isArray(apiDetail) ? apiDetail.map((d:any)=>d.msg).join("; ") : (e?.message || "Error"));
  } finally {
    saving.value = false;
  }
}

function clearForm() {
  playerId.value = null;
  gameId.value = null;
  Object.keys(form).forEach(key => {
    form[key as keyof typeof form] = 0;
  });
  msg.value = "";
}

async function load() {
  const [playersData, gamesData] = await Promise.all([listPlayers(), listGames()]);
  players.value = playersData.sort((a, b) => {
    if (a.first_name !== b.first_name) {
      return a.first_name.localeCompare(b.first_name);
    }
    return a.last_name.localeCompare(b.last_name);
  });
  games.value = gamesData;
}

onMounted(load);
</script>
