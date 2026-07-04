<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useEloStore } from '@/stores/elo'
import CurrentStandingsTable from '@/components/CurrentStandingsTable.vue'

const store = useEloStore()
onMounted(() => store.load())

const asOf = computed(() => {
  const race = store.latestRace()
  if (!race) return null
  const formatted = new Date(race.date).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
  return `${race.raceName} · ${formatted}`
})
</script>

<template>
  <section>
    <h1 class="text-3xl font-extrabold tracking-tight uppercase">Current Standings</h1>
    <p class="mt-2 text-sm text-neutral-400">
      Every driver on the current grid, ranked by their latest Elo rating.
    </p>
    <p v-if="asOf" class="mt-1 mb-8 text-xs text-neutral-500">
      Valid as of <span class="font-medium text-neutral-400">{{ asOf }}</span> — position and Elo movement
      shown vs. before that race.
    </p>

    <p v-if="store.loading" class="animate-pulse text-sm text-neutral-500">Loading standings…</p>
    <div v-else class="overflow-x-auto rounded-lg border border-neutral-800 bg-neutral-900">
      <CurrentStandingsTable />
    </div>
  </section>
</template>
