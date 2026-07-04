import { defineStore } from 'pinia'
import { ref } from 'vue'
import { parseCsv } from '@/lib/csv'
import type { AsOf, Driver, HistoryRow, StandingsRow } from '@/types/elo'

const START_ELO = 1000

export const useEloStore = defineStore('elo', () => {
  const drivers = ref<Driver[]>([])
  const driversByRef = ref(new Map<string, Driver>())
  const driversById = ref(new Map<number, Driver>())
  const history = ref<HistoryRow[]>([])
  const loaded = ref(false)
  const loading = ref(false)

  async function load() {
    if (loaded.value || loading.value) return
    loading.value = true

    const [driversText, historyText] = await Promise.all([
      fetch('/data/drivers.csv').then((r) => r.text()),
      fetch('/data/elo_history.csv').then((r) => r.text()),
    ])

    const [, ...driverBody] = parseCsv(driversText)
    drivers.value = driverBody.map(([driverId, name, driverRef]) => ({
      driverId: Number(driverId),
      name: name!,
      driverRef: driverRef!,
    }))
    for (const d of drivers.value) {
      driversByRef.value.set(d.driverRef, d)
      driversById.value.set(d.driverId, d)
    }

    const [, ...historyBody] = parseCsv(historyText)
    history.value = historyBody.map(
      ([driverId, date, raceName, qualiPos, finishPos, cat1, cat2, cat3, eloAfter]) => ({
        driverId: Number(driverId),
        date: date!,
        raceName: raceName!,
        qualiPos: qualiPos === '' ? null : Number(qualiPos),
        finishPos: finishPos === '' ? null : Number(finishPos),
        cat1Delta: Number(cat1),
        cat2Delta: Number(cat2),
        cat3Delta: Number(cat3),
        eloAfter: Number(eloAfter),
      }),
    )

    loading.value = false
    loaded.value = true
  }

  function historyFor(driverRef: string): HistoryRow[] {
    const driver = driversByRef.value.get(driverRef)
    if (!driver) return []
    return history.value.filter((h) => h.driverId === driver.driverId)
  }

  function latestRace(): AsOf | null {
    if (history.value.length === 0) return null
    const last = history.value[history.value.length - 1]!
    return { raceName: last.raceName, date: last.date }
  }

  function currentStandings(): StandingsRow[] {
    if (history.value.length === 0) return []

    // history.csv is already in chronological event order (how the notebook
    // builds and appends it) -- last occurrence per driver wins, no re-sort needed.
    // Track each driver's previous row too, to measure movement since their last race.
    const latestByDriver = new Map<number, HistoryRow>()
    const previousByDriver = new Map<number, HistoryRow>()
    for (const row of history.value) {
      const prior = latestByDriver.get(row.driverId)
      if (prior) previousByDriver.set(row.driverId, prior)
      latestByDriver.set(row.driverId, row)
    }

    const latestYear = Math.max(...history.value.map((h) => Number(h.date.slice(0, 4))))
    const current = [...latestByDriver.values()].filter(
      (row) => Number(row.date.slice(0, 4)) === latestYear,
    )

    // Rank the same set of drivers by their PREVIOUS Elo (debut drivers fall back
    // to the 1000 starting baseline) to get a "before this race" ordering to compare against.
    const previousEloByDriver = new Map<number, number>()
    for (const row of current) {
      previousEloByDriver.set(row.driverId, previousByDriver.get(row.driverId)?.eloAfter ?? START_ELO)
    }
    const previousRankByDriver = new Map<number, number>()
    ;[...current]
      .sort((a, b) => previousEloByDriver.get(b.driverId)! - previousEloByDriver.get(a.driverId)!)
      .forEach((row, i) => previousRankByDriver.set(row.driverId, i + 1))

    return [...current]
      .sort((a, b) => b.eloAfter - a.eloAfter)
      .map((row, i) => {
        const driver = driversById.value.get(row.driverId)!
        const rank = i + 1
        return {
          rank,
          driverId: row.driverId,
          name: driver.name,
          driverRef: driver.driverRef,
          elo: row.eloAfter,
          eloChange: row.cat1Delta + row.cat2Delta + row.cat3Delta,
          rankChange: previousRankByDriver.get(row.driverId)! - rank,
        }
      })
  }

  return { drivers, driversByRef, history, loaded, loading, load, historyFor, currentStandings, latestRace }
})
