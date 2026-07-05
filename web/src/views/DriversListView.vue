<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useEloStore } from '@/stores/elo'

const PAGE_SIZE = 20
const SEARCH_DEBOUNCE_MS = 400

const store = useEloStore()
onMounted(() => store.load())

const route = useRoute()
const router = useRouter()

function queryString(key: string): string {
  const value = route.query[key]
  return typeof value === 'string' ? value : ''
}

const searchTerm = ref(queryString('q'))
const page = ref(Number(queryString('page')) || 1)

let searchDebounce: ReturnType<typeof setTimeout> | undefined
onBeforeUnmount(() => clearTimeout(searchDebounce))

// true while local refs are being updated to mirror a URL change (e.g. back/forward),
// so those updates don't turn around and push/replace a navigation of their own
let syncingFromRoute = false

const filtered = computed(() => {
  const term = searchTerm.value.trim().toLowerCase()
  const ordered = store.driverListRows()
  if (!term) return ordered
  return ordered.filter(
    ({ driver: d }) =>
      d.name.toLowerCase().includes(term) ||
      d.driverRef.includes(term) ||
      d.code.toLowerCase().includes(term),
  )
})

const totalPages = computed(() => Math.max(1, Math.ceil(filtered.value.length / PAGE_SIZE)))

const paged = computed(() => {
  const start = (page.value - 1) * PAGE_SIZE
  return filtered.value.slice(start, start + PAGE_SIZE)
})

// filtering can shrink the result set out from under the current page
watch(filtered, () => {
  if (page.value > totalPages.value) page.value = totalPages.value
})

watch(searchTerm, (term) => {
  if (syncingFromRoute) return
  page.value = 1
  clearTimeout(searchDebounce)
  searchDebounce = setTimeout(() => {
    router.push({ query: { ...route.query, q: term.trim() || undefined } })
  }, SEARCH_DEBOUNCE_MS)
})

watch(page, (p) => {
  if (syncingFromRoute) return
  router.replace({ query: { ...route.query, page: p > 1 ? String(p) : undefined } })
})

// back/forward navigation restores state from the URL rather than pushing again
watch(
  () => route.query,
  (query) => {
    syncingFromRoute = true
    const q = typeof query.q === 'string' ? query.q : ''
    const p = Number(query.page) || 1
    if (q !== searchTerm.value) searchTerm.value = q
    if (p !== page.value) page.value = p
    nextTick(() => {
      syncingFromRoute = false
    })
  },
)
</script>

<template>
  <section>
    <h1 class="text-3xl font-extrabold tracking-tight uppercase">Driver Lookup</h1>
    <p class="mt-2 mb-6 text-sm text-neutral-400">Search or browse every driver in the dataset.</p>

    <input
      v-model="searchTerm"
      type="text"
      placeholder="Search by name or code..."
      class="mb-6 w-full max-w-sm rounded-md border border-neutral-800 bg-neutral-900 px-3 py-2.5 text-sm font-medium text-neutral-100 placeholder-neutral-500 outline-none focus:border-[#E10600] focus:ring-1 focus:ring-[#E10600]"
    />

    <p v-if="store.loading" class="animate-pulse text-sm text-neutral-500">Loading…</p>
    <template v-else>
      <div class="overflow-hidden rounded-lg border border-neutral-800 bg-neutral-900">
        <div
          class="grid grid-cols-[2fr_1fr_1.3fr_64px_64px] gap-4 border-b border-neutral-800/80 px-5 py-1.5 text-xs font-medium tracking-wide text-neutral-500 uppercase"
        >
          <span>Driver</span>
          <span>Team</span>
          <span>Last GP</span>
          <span class="text-right">Elo</span>
          <span class="text-right">Races</span>
        </div>
        <RouterLink
          v-for="row in paged"
          :key="row.driver.driverId"
          :to="{ name: 'driver', params: { driverRef: row.driver.driverRef } }"
          class="grid grid-cols-[2fr_1fr_1.3fr_64px_64px] items-center gap-4 border-b border-neutral-800/50 px-5 py-2.5 transition-colors last:border-0 hover:bg-white/5"
        >
          <div class="min-w-0">
            <div class="flex items-center gap-2">
              <span class="font-semibold">{{ row.driver.name }}</span>
              <span
                v-if="row.driver.number != null"
                class="text-xs font-bold tabular-nums text-neutral-500"
              >
                #{{ row.driver.number }}
              </span>
            </div>
            <div class="mt-0.5 truncate text-xs text-neutral-400">
              {{ row.driver.code }} · {{ row.driver.nationality }}
            </div>
          </div>
          <div class="truncate text-sm text-neutral-300">{{ row.team }}</div>
          <div class="truncate text-sm text-neutral-300">
            <span v-if="row.lastRaceYear">{{ row.lastRaceYear }} {{ row.lastRaceName }}</span>
            <span v-else>—</span>
          </div>
          <div class="text-right font-bold tabular-nums">{{ row.elo }}</div>
          <div class="text-right font-bold tabular-nums">{{ row.raceCount }}</div>
        </RouterLink>
        <p v-if="filtered.length === 0" class="px-5 py-6 text-sm text-neutral-500">No drivers found.</p>
      </div>

      <div v-if="filtered.length > 0" class="mt-4 flex items-center justify-between text-sm">
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
  </section>
</template>
