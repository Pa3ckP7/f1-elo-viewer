<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="flex min-h-screen bg-neutral-950 text-neutral-100">
    <aside class="sticky top-0 flex h-screen w-56 shrink-0 flex-col border-r border-neutral-800">
      <div class="border-b border-neutral-800 px-5 py-5">
        <span class="text-xl font-black tracking-tight uppercase">
          F1 <span class="text-[#E10600]">Elo</span>
        </span>
        <div class="mt-1 text-xs text-neutral-500">Driver ratings since 1970</div>
      </div>
      <nav class="flex flex-col gap-1 p-3">
        <RouterLink
          to="/"
          class="rounded-md border-l-2 border-transparent px-3 py-2 text-sm text-neutral-300 transition-colors hover:bg-white/5 hover:text-white"
          active-class="border-[#E10600] bg-white/5 text-white"
        >
          Standings
        </RouterLink>
        <RouterLink
          to="/drivers"
          class="rounded-md border-l-2 border-transparent px-3 py-2 text-sm text-neutral-300 transition-colors hover:bg-white/5 hover:text-white"
          active-class="border-[#E10600] bg-white/5 text-white"
        >
          Driver Lookup
        </RouterLink>
      </nav>
    </aside>
    <main class="min-w-0 flex-1 px-8 py-10">
      <div class="mx-auto max-w-4xl">
        <RouterView />
      </div>
    </main>
  </div>
</template>
