<script setup lang="ts">
import type { HistoryRow } from '@/types/elo'

defineProps<{ rows: HistoryRow[] }>()

function signed(n: number): string {
  if (n === 0) return '0'
  return n > 0 ? `+${n}` : `${n}`
}

function deltaClass(n: number): string {
  if (n > 0) return 'text-emerald-400'
  if (n < 0) return 'text-red-400'
  return 'text-neutral-600'
}
</script>

<template>
  <table class="w-full min-w-[700px] text-left text-sm">
    <thead>
      <tr class="border-b border-neutral-800 text-xs font-bold tracking-widest text-neutral-500 uppercase">
        <th class="py-3 pr-4 pl-4">Date</th>
        <th class="py-3 pr-4">Race</th>
        <th class="py-3 pr-4">Quali</th>
        <th class="py-3 pr-4">Finish</th>
        <th class="py-3 pr-4">Cat 1</th>
        <th class="py-3 pr-4">Cat 2</th>
        <th class="py-3 pr-4">Cat 3</th>
        <th class="py-3 pr-4">Elo</th>
      </tr>
    </thead>
    <tbody>
      <tr
        v-for="(row, i) in rows"
        :key="i"
        class="border-b border-neutral-800/60 transition-colors last:border-0 hover:bg-neutral-900"
      >
        <td class="py-2.5 pr-4 pl-4 whitespace-nowrap text-neutral-500">{{ row.date }}</td>
        <td class="py-2.5 pr-4 font-medium">{{ row.raceName }}</td>
        <td class="py-2.5 pr-4 tabular-nums text-neutral-400">{{ row.qualiPos ?? '—' }}</td>
        <td class="py-2.5 pr-4 tabular-nums text-neutral-400">{{ row.finishPos ?? '—' }}</td>
        <td class="py-2.5 pr-4 tabular-nums" :class="deltaClass(row.cat1Delta)">{{ signed(row.cat1Delta) }}</td>
        <td class="py-2.5 pr-4 tabular-nums" :class="deltaClass(row.cat2Delta)">{{ signed(row.cat2Delta) }}</td>
        <td class="py-2.5 pr-4 tabular-nums" :class="deltaClass(row.cat3Delta)">{{ signed(row.cat3Delta) }}</td>
        <td class="py-2.5 pr-4 text-base font-black tabular-nums">{{ Math.round(row.eloAfter) }}</td>
      </tr>
    </tbody>
  </table>
</template>
