<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="min-h-screen bg-neutral-950 text-neutral-100">
    <div class="h-1.5 bg-[#E10600]" />
    <header class="sticky top-0 z-20 border-b border-neutral-800 bg-neutral-950/90 backdrop-blur">
      <div class="mx-auto flex max-w-5xl items-baseline justify-between px-4 py-4">
        <span class="text-xl font-black tracking-tight uppercase">
          F1 <span class="text-[#E10600]">Elo</span>
        </span>
        <span class="hidden text-xs text-neutral-500 sm:inline">Driver ratings since 1970</span>
      </div>
      <nav class="mx-auto flex max-w-5xl gap-8 px-4">
        <RouterLink
          to="/"
          class="border-b-2 border-transparent py-3 text-sm text-neutral-300 transition-colors hover:text-white"
          active-class="border-[#E10600] text-white"
        >
          Standings
        </RouterLink>
        <RouterLink
          to="/drivers"
          class="border-b-2 border-transparent py-3 text-sm text-neutral-300 transition-colors hover:text-white"
          active-class="border-[#E10600] text-white"
        >
          Driver Lookup
        </RouterLink>
      </nav>
    </header>
    <main class="mx-auto max-w-5xl px-4 py-10">
      <RouterView />
    </main>
  </div>
</template>
