<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  ComboboxAnchor,
  ComboboxContent,
  ComboboxEmpty,
  ComboboxInput,
  ComboboxItem,
  ComboboxPortal,
  ComboboxRoot,
  ComboboxViewport,
} from 'reka-ui'
import { useEloStore } from '@/stores/elo'

const store = useEloStore()
const router = useRouter()
const searchTerm = ref('')

const filtered = computed(() => {
  const term = searchTerm.value.trim().toLowerCase()
  if (!term) return store.drivers.slice(0, 20)
  return store.drivers
    .filter((d) => d.name.toLowerCase().includes(term) || d.driverRef.includes(term))
    .slice(0, 20)
})

function onSelect(driverRef: unknown) {
  if (typeof driverRef === 'string') {
    router.push({ name: 'driver', params: { driverRef } })
  }
}
</script>

<template>
  <ComboboxRoot :model-value="null" @update:model-value="onSelect">
    <ComboboxAnchor class="relative block">
      <svg
        viewBox="0 0 20 20"
        fill="currentColor"
        class="pointer-events-none absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-neutral-500"
      >
        <path
          fill-rule="evenodd"
          d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z"
          clip-rule="evenodd"
        />
      </svg>
      <ComboboxInput
        v-model="searchTerm"
        placeholder="Search for a driver..."
        class="w-full rounded-md border border-neutral-800 bg-neutral-900 py-2.5 pr-3 pl-9 text-sm font-medium text-neutral-100 placeholder-neutral-500 outline-none focus:border-[#E10600] focus:ring-1 focus:ring-[#E10600]"
      />
    </ComboboxAnchor>
    <ComboboxPortal>
      <ComboboxContent
        class="z-30 mt-2 max-h-72 overflow-hidden rounded-md border border-neutral-800 bg-neutral-900 shadow-xl shadow-black/50"
      >
        <ComboboxViewport class="p-1">
          <ComboboxEmpty class="px-3 py-2 text-sm text-neutral-500">No drivers found.</ComboboxEmpty>
          <ComboboxItem
            v-for="driver in filtered"
            :key="driver.driverId"
            :value="driver.driverRef"
            class="cursor-pointer rounded-sm px-3 py-2 text-sm font-medium outline-none data-[highlighted]:bg-neutral-800"
          >
            {{ driver.name }}
          </ComboboxItem>
        </ComboboxViewport>
      </ComboboxContent>
    </ComboboxPortal>
  </ComboboxRoot>
</template>
