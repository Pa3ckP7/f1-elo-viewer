<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useEloStore } from '@/stores/elo'

const store = useEloStore()
onMounted(() => store.load())

const searchTerm = ref('')

const filtered = computed(() => {
  const term = searchTerm.value.trim().toLowerCase()
  const ordered = store.driversByRecency()
  if (!term) return ordered
  return ordered.filter(
    (d) =>
      d.name.toLowerCase().includes(term) ||
      d.driverRef.includes(term) ||
      d.code.toLowerCase().includes(term),
  )
})
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
    <div v-else class="overflow-hidden rounded-lg border border-neutral-800 bg-neutral-900">
      <RouterLink
        v-for="driver in filtered"
        :key="driver.driverId"
        :to="{ name: 'driver', params: { driverRef: driver.driverRef } }"
        class="flex items-center justify-between gap-4 border-b border-neutral-800/50 px-5 py-2.5 transition-colors last:border-0 hover:bg-white/5"
      >
        <span class="font-semibold">{{ driver.name }}</span>
        <span class="shrink-0 text-xs text-neutral-400">{{ driver.code }} · {{ driver.nationality }}</span>
      </RouterLink>
      <p v-if="filtered.length === 0" class="px-5 py-6 text-sm text-neutral-500">No drivers found.</p>
    </div>
  </section>
</template>
