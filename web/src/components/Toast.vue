<template>
  <transition name="fade">
    <div v-if="show" class="fixed bottom-4 left-1/2 -translate-x-1/2 bg-black text-white text-sm px-4 py-2 rounded-xl shadow-lg">
      {{ message }}
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref } from "vue";
const show = ref(false);
const message = ref("");
function open(msg: string, ms = 2000){ message.value = msg; show.value = true; setTimeout(()=> show.value=false, ms); }
defineExpose({ open });
</script>

<style>
.fade-enter-active,.fade-leave-active{ transition: opacity .2s; }
.fade-enter-from,.fade-leave-to{ opacity:0; }
</style>
