<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useEloStore } from '@/stores/elo'
import DriverSearch from '@/components/DriverSearch.vue'
import DriverHistoryTable from '@/components/DriverHistoryTable.vue'

const props = defineProps<{ driverRef?: string }>()

const store = useEloStore()
onMounted(() => store.load())

const driver = computed(() => (props.driverRef ? store.driversByRef.get(props.driverRef) : undefined))
const history = computed(() => (props.driverRef ? store.historyFor(props.driverRef) : []))
</script>

<template>
  <section>
    <h1 class="text-3xl font-extrabold tracking-tight uppercase">Race History</h1>
    <p class="mt-2 mb-8 text-sm text-neutral-400">Search any driver to see their full race-by-race Elo history.</p>

    <DriverSearch class="mb-8 max-w-sm" />

    <p v-if="store.loading" class="animate-pulse text-sm text-neutral-500">Loading…</p>
    <template v-else-if="props.driverRef">
      <h2 v-if="driver" class="mb-3 text-xl font-bold">{{ driver.name }}</h2>
      <div class="overflow-x-auto rounded-lg border border-neutral-800 bg-neutral-900">
        <DriverHistoryTable :rows="history" />
      </div>
    </template>
    <p v-else class="text-sm text-neutral-500">
      Search for a driver above to see their full race-by-race Elo history.
    </p>
  </section>
</template>
