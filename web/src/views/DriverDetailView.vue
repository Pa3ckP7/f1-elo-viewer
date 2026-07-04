<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useEloStore } from '@/stores/elo'
import DriverHistoryTable from '@/components/DriverHistoryTable.vue'

const props = defineProps<{ driverRef: string }>()

const store = useEloStore()
onMounted(() => store.load())

const summary = computed(() => store.driverSummary(props.driverRef))
const historyNewestFirst = computed(() => [...store.historyFor(props.driverRef)].reverse())

function formatDate(date: string): string {
  return new Date(date).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
}

function yearOf(date: string): string {
  return date.slice(0, 4)
}
</script>

<template>
  <section>
    <RouterLink
      :to="{ name: 'drivers-list' }"
      class="mb-4 inline-flex items-center gap-1.5 text-sm text-neutral-400 transition-colors hover:text-white"
    >
      ← Back to Drivers
    </RouterLink>

    <p v-if="store.loading" class="animate-pulse text-sm text-neutral-500">Loading…</p>
    <template v-else-if="summary">
      <div class="mb-8 rounded-lg border border-neutral-800 bg-neutral-900 p-8">
        <div class="flex flex-wrap items-start justify-between gap-8">
          <div>
            <h1 class="text-4xl font-black tracking-tight">{{ summary.driver.name }}</h1>
            <p class="mt-2 text-base text-neutral-400">
              {{ summary.driver.code }} · {{ summary.driver.nationality }}
              <span v-if="summary.driver.number != null"> · No. {{ summary.driver.number }}</span>
            </p>
            <p class="mt-1 text-base font-medium text-neutral-300">{{ summary.currentTeam }}</p>
          </div>
          <div class="flex gap-10">
            <div class="text-right">
              <div class="text-4xl font-black tabular-nums">{{ summary.currentElo }}</div>
              <div class="mt-1 text-xs font-semibold tracking-widest text-neutral-300 uppercase">Current Elo</div>
            </div>
            <div class="text-right">
              <div class="text-4xl font-black tabular-nums text-red-300">{{ summary.peakElo }}</div>
              <div class="mt-1 text-xs font-semibold tracking-widest text-neutral-300 uppercase">Peak Elo</div>
            </div>
          </div>
        </div>
        <div class="mt-8 grid grid-cols-2 gap-6 border-t border-neutral-800 pt-6 sm:grid-cols-3 lg:grid-cols-5">
          <div>
            <div class="text-xl font-bold tabular-nums">{{ summary.raceCount }}</div>
            <div class="mt-0.5 text-xs font-semibold tracking-widest text-neutral-300 uppercase">Races</div>
          </div>
          <div>
            <div class="text-xl font-bold tabular-nums">{{ summary.wins }}</div>
            <div class="mt-0.5 text-xs font-semibold tracking-widest text-neutral-300 uppercase">Wins</div>
          </div>
          <div>
            <div class="text-xl font-bold tabular-nums">{{ summary.podiums }}</div>
            <div class="mt-0.5 text-xs font-semibold tracking-widest text-neutral-300 uppercase">Podiums</div>
          </div>
          <div>
            <div class="text-xl font-bold">{{ summary.debutRaceName }}</div>
            <div class="mt-0.5 text-xs font-semibold tracking-widest text-neutral-300 uppercase">
              Debut · {{ yearOf(summary.debutDate) }}
            </div>
          </div>
          <div>
            <div class="text-xl font-bold">{{ summary.peakRaceName }}</div>
            <div class="mt-0.5 text-xs font-semibold tracking-widest text-neutral-300 uppercase">
              Peak race · {{ formatDate(summary.peakDate) }}
            </div>
          </div>
        </div>
      </div>

      <h2 class="mb-3 text-lg font-bold">Race History</h2>
      <div class="overflow-x-auto rounded-lg border border-neutral-800 bg-neutral-900">
        <DriverHistoryTable :rows="historyNewestFirst" />
      </div>
    </template>
    <p v-else class="text-sm text-neutral-500">Driver not found.</p>
  </section>
</template>
