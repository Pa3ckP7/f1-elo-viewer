<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useEloStore } from '@/stores/elo'
import DriverHistoryTable from '@/components/DriverHistoryTable.vue'

const PAGE_SIZE = 10

const props = defineProps<{ driverRef: string }>()

const store = useEloStore()
onMounted(() => store.load())

const route = useRoute()
const router = useRouter()

const page = ref(Number(route.query.page) || 1)

const summary = computed(() => store.driverSummary(props.driverRef))
const historyNewestFirst = computed(() => [...store.historyFor(props.driverRef)].reverse())

const totalPages = computed(() => Math.max(1, Math.ceil(historyNewestFirst.value.length / PAGE_SIZE)))

const paged = computed(() => {
  const start = (page.value - 1) * PAGE_SIZE
  return historyNewestFirst.value.slice(start, start + PAGE_SIZE)
})

// switching to a different driver starts back at page 1 rather than keeping a stale page number
watch(
  () => props.driverRef,
  () => {
    page.value = 1
  },
)

// a page number from the URL can be out of range for this driver's race count
watch(historyNewestFirst, () => {
  if (page.value > totalPages.value) page.value = totalPages.value
})

watch(page, (p) => {
  router.replace({ query: { ...route.query, page: p > 1 ? String(p) : undefined } })
})

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
        <div class="mt-8 grid max-w-xs grid-cols-3 gap-6 border-t border-neutral-800 pt-6">
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
        </div>
        <div class="mt-6 grid grid-cols-1 gap-6 sm:grid-cols-2">
          <div>
            <div class="text-xl font-bold">{{ yearOf(summary.debutDate) }} {{ summary.debutRaceName }}</div>
            <div class="mt-0.5 text-xs font-semibold tracking-widest text-neutral-300 uppercase">Debut</div>
          </div>
          <div>
            <div class="text-xl font-bold">{{ yearOf(summary.peakDate) }} {{ summary.peakRaceName }}</div>
            <div class="mt-0.5 text-xs font-semibold tracking-widest text-neutral-300 uppercase">Peak race</div>
          </div>
        </div>
      </div>

      <h2 class="mb-3 text-lg font-bold">Race History</h2>
      <div class="overflow-x-auto rounded-lg border border-neutral-800 bg-neutral-900">
        <DriverHistoryTable :rows="paged" />
      </div>

      <div v-if="historyNewestFirst.length > 0" class="mt-4 flex items-center justify-between text-sm">
        <button
          type="button"
          :disabled="page <= 1"
          class="rounded-md border border-neutral-800 px-3 py-1.5 font-medium text-neutral-300 transition-colors hover:bg-white/5 hover:text-white disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-transparent"
          @click="page--"
        >
          ← Prev
        </button>
        <span class="text-xs text-neutral-500">Page {{ page }} of {{ totalPages }}</span>
        <button
          type="button"
          :disabled="page >= totalPages"
          class="rounded-md border border-neutral-800 px-3 py-1.5 font-medium text-neutral-300 transition-colors hover:bg-white/5 hover:text-white disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-transparent"
          @click="page++"
        >
          Next →
        </button>
      </div>
    </template>
    <p v-else class="text-sm text-neutral-500">Driver not found.</p>
  </section>
</template>
