import { createRouter, createWebHistory } from "vue-router";
import Home from "./pages/Home.vue";
import Login from "./pages/Login.vue";
import Players from "./pages/Players.vue";
import Games from "./pages/Games.vue";
import Stats from "./pages/Stats.vue";
import PlayerDetail from "./pages/PlayerDetail.vue";
import GameDetail from "./pages/GameDetail.vue";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: Home },
    { path: "/login", component: Login },
    { path: "/players", component: Players },
    { path: "/players/:id", component: PlayerDetail },
    { path: "/games", component: Games },
    { path: "/games/:id", component: GameDetail },
    { path: "/stats", component: Stats },
  ],
});
