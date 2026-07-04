<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useEloStore } from '@/stores/elo'

const store = useEloStore()
const rows = computed(() => store.currentStandings())

function signed(n: number): string {
  if (n === 0) return '0'
  return n > 0 ? `+${n}` : `${n}`
}
</script>

<template>
  <table class="w-full text-left text-sm">
    <thead>
      <tr class="border-b border-neutral-800/80 text-xs tracking-wide text-neutral-500 uppercase">
        <th class="py-3 pr-4 pl-5 font-medium">Pos.</th>
        <th class="py-3 pr-4 font-medium">Driver</th>
        <th class="py-3 pr-5 text-right font-medium">Elo</th>
      </tr>
    </thead>
    <tbody>
      <tr
        v-for="row in rows"
        :key="row.driverId"
        class="border-b border-neutral-800/50 transition-colors last:border-0 hover:bg-white/5"
      >
        <td class="py-3.5 pr-4 pl-5">
          <div class="flex items-center gap-2">
            <span class="font-bold tabular-nums text-neutral-400">{{ row.rank }}</span>
            <span
              v-if="row.rankChange > 0"
              class="flex items-center text-xs font-semibold tabular-nums text-emerald-400"
              :title="`Up ${row.rankChange} since last race`"
            >
              ▲{{ row.rankChange }}
            </span>
            <span
              v-else-if="row.rankChange < 0"
              class="flex items-center text-xs font-semibold tabular-nums text-red-400"
              :title="`Down ${-row.rankChange} since last race`"
            >
              ▼{{ -row.rankChange }}
            </span>
            <span v-else class="text-xs text-neutral-600" title="No change since last race">—</span>
          </div>
        </td>
        <td class="py-3.5 pr-4">
          <RouterLink :to="{ name: 'driver', params: { driverRef: row.driverRef } }" class="font-semibold hover:underline">
            {{ row.name }}
          </RouterLink>
        </td>
        <td class="py-3.5 pr-5 text-right">
          <div class="flex items-baseline justify-end gap-2">
            <span class="font-bold tabular-nums">{{ Math.round(row.elo) }}</span>
            <span
              class="text-xs tabular-nums"
              :class="row.eloChange > 0 ? 'text-emerald-400' : row.eloChange < 0 ? 'text-red-400' : 'text-neutral-600'"
            >
              {{ signed(row.eloChange) }}
            </span>
          </div>
        </td>
      </tr>
    </tbody>
  </table>
</template>
