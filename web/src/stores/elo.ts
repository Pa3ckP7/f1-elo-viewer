import { defineStore } from 'pinia'
import { ref } from 'vue'
import { parseCsv } from '@/lib/csv'
import type { AsOf, Driver, DriverSummary, HistoryRow, StandingsRow } from '@/types/elo'

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
    drivers.value = driverBody.map(([driverId, name, driverRef, code, number, nationality]) => ({
      driverId: Number(driverId),
      name: name!,
      driverRef: driverRef!,
      code: code!,
      number: number === '' ? null : Number(number),
      nationality: nationality!,
    }))
    for (const d of drivers.value) {
      driversByRef.value.set(d.driverRef, d)
      driversById.value.set(d.driverId, d)
    }

    const [, ...historyBody] = parseCsv(historyText)
    history.value = historyBody.map(
      ([driverId, date, raceName, team, qualiPos, finishPos, cat1, cat2, cat3, eloAfter]) => ({
        driverId: Number(driverId),
        date: date!,
        raceName: raceName!,
        team: team!,
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

  function driverSummary(driverRef: string): DriverSummary | null {
    const driver = driversByRef.value.get(driverRef)
    const rows = historyFor(driverRef) // already chronological, oldest first
    if (!driver || rows.length === 0) return null

    const first = rows[0]!
    const last = rows[rows.length - 1]!
    const peak = rows.reduce((max, r) => (r.eloAfter > max.eloAfter ? r : max), rows[0]!)

    // wins/podiums are main-race-only -- sprint rows are tagged " (Sprint)" in raceName
    const raceRows = rows.filter((r) => !r.raceName.endsWith('(Sprint)'))
    const wins = raceRows.filter((r) => r.finishPos === 1).length
    const podiums = raceRows.filter((r) => r.finishPos !== null && r.finishPos <= 3).length

    return {
      driver,
      currentTeam: last.team,
      currentElo: last.eloAfter,
      peakElo: peak.eloAfter,
      peakRaceName: peak.raceName,
      peakDate: peak.date,
      raceCount: rows.length,
      debutDate: first.date,
      debutRaceName: first.raceName,
      wins,
      podiums,
    }
  }

  function driversByRecency(): Driver[] {
    // last row per driver = their most recent participation (history.csv is
    // already chronological, so last occurrence wins, no re-sort needed)
    const lastRowByDriver = new Map<number, HistoryRow>()
    for (const row of history.value) {
      lastRowByDriver.set(row.driverId, row)
    }

    return [...drivers.value].sort((a, b) => {
      const rowA = lastRowByDriver.get(a.driverId)
      const rowB = lastRowByDriver.get(b.driverId)
      if (!rowA || !rowB) return 0
      if (rowA.date !== rowB.date) return rowB.date.localeCompare(rowA.date) // most recent race first
      return (rowA.finishPos ?? Infinity) - (rowB.finishPos ?? Infinity) // then position in that race
    })
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
          code: driver.code,
          number: driver.number,
          nationality: driver.nationality,
          team: row.team,
          elo: row.eloAfter,
          eloChange: row.cat1Delta + row.cat2Delta + row.cat3Delta,
          rankChange: previousRankByDriver.get(row.driverId)! - rank,
        }
      })
  }

  return {
    drivers,
    driversByRef,
    history,
    loaded,
    loading,
    load,
    historyFor,
    currentStandings,
    latestRace,
    driverSummary,
    driversByRecency,
  }
})
