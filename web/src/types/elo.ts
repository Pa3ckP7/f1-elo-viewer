export interface Driver {
  driverId: number
  name: string
  driverRef: string
}

export interface HistoryRow {
  driverId: number
  date: string
  raceName: string
  qualiPos: number | null
  finishPos: number | null
  cat1Delta: number
  cat2Delta: number
  cat3Delta: number
  eloAfter: number
}

export interface StandingsRow {
  rank: number
  driverId: number
  name: string
  driverRef: string
  elo: number
  /** Elo gained/lost in the driver's most recent race (their last row's own deltas). */
  eloChange: number
  /** Position change vs. the standings as they stood before the most recent race,
   * ranked among the same current-grid drivers (positive = moved up). A driver's
   * debut race compares against the 1000 starting baseline. */
  rankChange: number
}

export interface AsOf {
  raceName: string
  date: string
}
