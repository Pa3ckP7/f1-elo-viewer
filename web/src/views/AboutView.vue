<script setup lang="ts">
import { RouterLink } from 'vue-router'
import Katex from '@/components/Katex.vue'
</script>

<template>
  <section>
    <h1 class="text-3xl font-extrabold tracking-tight uppercase">How It Works</h1>
    <p class="mt-2 mb-6 max-w-2xl text-sm text-neutral-400">
      What this project is, how the Elo rating is built, and what each category actually measures.
    </p>

    <!-- small screens: no room for a side rail, fall back to an inline jump-link row -->
    <nav class="mb-8 rounded-lg border border-neutral-800 bg-neutral-900 p-5 lg:hidden">
      <p class="text-xs font-semibold tracking-widest text-neutral-500 uppercase">On this page</p>
      <ul class="mt-3 flex flex-wrap gap-x-6 gap-y-2 text-sm">
        <li><a href="#what-is-this" class="text-neutral-300 hover:text-white">What is this?</a></li>
        <li><a href="#how-elo-works" class="text-neutral-300 hover:text-white">How an Elo rating works</a></li>
        <li><a href="#categories" class="text-neutral-300 hover:text-white">Three categories, every race</a></li>
        <li><a href="#special-cases" class="text-neutral-300 hover:text-white">Special cases</a></li>
        <li><a href="#interpreting-ratings" class="text-neutral-300 hover:text-white">Interpreting the ratings</a></li>
        <li><a href="#scope-data" class="text-neutral-300 hover:text-white">Scope &amp; data</a></li>
      </ul>
    </nav>

    <div class="flex items-start gap-8">
      <nav class="sticky top-10 hidden w-44 shrink-0 lg:block">
        <p class="text-xs font-semibold tracking-widest text-neutral-500 uppercase">On this page</p>
        <ul class="mt-3 space-y-2 text-sm">
          <li><a href="#what-is-this" class="text-neutral-300 hover:text-white">What is this?</a></li>
          <li><a href="#how-elo-works" class="text-neutral-300 hover:text-white">How an Elo rating works</a></li>
          <li><a href="#categories" class="text-neutral-300 hover:text-white">Three categories, every race</a></li>
          <li><a href="#special-cases" class="text-neutral-300 hover:text-white">Special cases</a></li>
          <li><a href="#interpreting-ratings" class="text-neutral-300 hover:text-white">Interpreting the ratings</a></li>
          <li><a href="#scope-data" class="text-neutral-300 hover:text-white">Scope &amp; data</a></li>
        </ul>
      </nav>

      <div class="min-w-0 flex-1 space-y-6">
      <section id="what-is-this" class="scroll-mt-6 rounded-lg border border-neutral-800 bg-neutral-900 p-8">
        <h2 class="text-lg font-bold">What is this?</h2>
        <p class="mt-3 max-w-3xl text-sm leading-relaxed text-neutral-300">
          Every driver who has started an F1 race since 1970 is given a custom Elo rating that updates after
          every Grand Prix. Instead of just tracking championship points, it compares each driver against the
          rivals directly relevant to them in a given race — who they out-qualified, who they passed (or were
          passed by) on track, and who they beat to the flag — so a strong drive in a slow car counts for
          something even without points to show for it.
        </p>
        <p class="mt-3 max-w-3xl text-sm leading-relaxed text-neutral-300">
          <strong class="text-neutral-100">Current Standings</strong> shows every driver on the latest grid
          ranked by rating today; <strong class="text-neutral-100">Driver Lookup</strong> shows any driver's
          full career, race by race.
        </p>
      </section>

      <section id="how-elo-works" class="scroll-mt-6 rounded-lg border border-neutral-800 bg-neutral-900 p-8">
        <h2 class="text-lg font-bold">How an Elo rating works</h2>
        <p class="mt-3 max-w-3xl text-sm leading-relaxed text-neutral-300">
          Elo is borrowed from competitive chess. Every driver starts at
          <span class="font-semibold text-neutral-100">1000</span>. Before any result is known, the gap
          between two drivers' ratings converts into an "expected score" — roughly, the probability the
          higher-rated driver comes out ahead:
        </p>
        <div class="mt-4 overflow-x-auto rounded-md border border-neutral-800 bg-neutral-950 p-4 text-neutral-100">
          <Katex display expr="E_{AB} = \dfrac{1}{1 + 10^{(R_B - R_A)/400}}" />
        </div>
        <div class="mt-3 flex flex-wrap gap-x-10 gap-y-3 overflow-x-auto rounded-md border border-neutral-800 bg-neutral-950 p-4 text-neutral-100">
          <div>
            <span class="mr-2 text-xs font-semibold tracking-widest text-neutral-500 uppercase">win</span>
            <Katex expr="\Delta = K(1 - E_{AB})" />
          </div>
          <div>
            <span class="mr-2 text-xs font-semibold tracking-widest text-neutral-500 uppercase">loss</span>
            <Katex expr="\Delta = -K \cdot E_{AB}" />
          </div>
        </div>
        <p class="mt-4 max-w-3xl text-sm leading-relaxed text-neutral-300">
          <span class="font-semibold text-neutral-100">K</span> just scales how big a swing any single result
          can cause. The bigger the rating gap, the smaller the reward for the favourite winning as expected —
          and the bigger the reward for the underdog pulling off the upset.
        </p>
        <div class="mt-4 grid gap-4 sm:grid-cols-2">
          <div class="rounded-md border border-neutral-800 bg-neutral-950 p-4 text-sm">
            <p class="font-semibold text-neutral-100">Evenly matched (1000 vs 1000)</p>
            <p class="mt-2 text-neutral-300"><Katex expr="E_{AB} = 0.5" /></p>
            <p class="mt-2 text-neutral-300">
              Winner gains <Katex expr="\Delta = K(1 - 0.5) = \dfrac{K}{2}" />
            </p>
          </div>
          <div class="rounded-md border border-neutral-800 bg-neutral-950 p-4 text-sm">
            <p class="font-semibold text-neutral-100">Favourite (1200) vs underdog (1000)</p>
            <p class="mt-2 text-neutral-300"><Katex expr="E_{\text{fav}} \approx 0.76" /></p>
            <p class="mt-2 text-neutral-300">
              Favourite wins → <Katex expr="\Delta = 32(1 - 0.76) \approx" />
              <span class="text-emerald-400"><Katex expr="+8" /></span>
              <span class="text-neutral-500">(expected result, small reward)</span>
            </p>
            <p class="mt-2 text-neutral-300">
              Underdog wins → <Katex expr="\Delta = 32(1 - 0.24) \approx" />
              <span class="text-emerald-400"><Katex expr="+24" /></span>
              <span class="text-neutral-500">(upset, big reward)</span>
            </p>
          </div>
        </div>
        <p class="mt-4 max-w-3xl text-sm leading-relaxed text-neutral-300">
          Each driver's delta is worked out purely from their own side of the matchup — a rival's rating is
          only ever an input to that formula, never something updated automatically as a mirror image. Combined
          with the exclusion rules below (retirements, disqualifications), that means the total rating in the
          system isn't a fixed pool being shuffled around — it can drift up or down over time.
        </p>
      </section>

      <section id="categories" class="scroll-mt-6 rounded-lg border border-neutral-800 bg-neutral-900 p-8">
        <h2 class="text-lg font-bold">Three categories, every race</h2>
        <p class="mt-3 max-w-3xl text-sm leading-relaxed text-neutral-300">
          All three categories use each driver's rating <em>going into</em> the race — none of them see each
          other's results mid-calculation. The three deltas are rounded to whole numbers and summed once,
          after the race, to produce the new rating.
        </p>

        <div class="mt-6 space-y-6">
          <div class="border-t border-neutral-800 pt-6">
            <div class="flex flex-wrap items-baseline justify-between gap-2">
              <h3 class="font-semibold text-neutral-100">1 · Qualifying position</h3>
              <span class="text-xs font-semibold tracking-widest text-neutral-500 uppercase">K = 32</span>
            </div>
            <p class="mt-2 max-w-3xl text-sm leading-relaxed text-neutral-300">
              Each driver is compared against whoever qualified one place above and one place below them —
              a win against the driver behind, a loss to the driver ahead. A driver with no recorded qualifying
              time (common before the mid-1990s, or a no-time DQ) gets a delta of 0 for this category.
            </p>
            <div class="mt-3 rounded-md border border-neutral-800 bg-neutral-950 p-4 text-sm text-neutral-400">
              <p class="font-semibold text-neutral-100">Example</p>
              <p class="mt-1">
                P3 (rated 980) out-qualified P4 (rated 1100, a big upset) but was out-qualified by P2 (rated
                1000, a close call):
              </p>
              <p class="mt-2 text-neutral-300">
                beats P4: <Katex expr="\Delta = 32(1 - 0.334) \approx" />
                <span class="text-emerald-400"><Katex expr="+21" /></span>
              </p>
              <p class="mt-2 text-neutral-300">
                loses to P2: <Katex expr="\Delta = 32(0 - 0.471) \approx" />
                <span class="text-red-400"><Katex expr="-15" /></span>
              </p>
              <p class="mt-2">
                net <span class="text-emerald-400">+6</span> — out-qualifying a much stronger car counts for
                more than narrowly losing out to a similarly-rated one.
              </p>
            </div>
          </div>

          <div class="border-t border-neutral-800 pt-6">
            <div class="flex flex-wrap items-baseline justify-between gap-2">
              <h3 class="font-semibold text-neutral-100">2 · Grid vs. race result</h3>
              <span class="text-xs font-semibold tracking-widest text-neutral-500 uppercase">K = 16 (half weight)</span>
            </div>
            <p class="mt-2 max-w-3xl text-sm leading-relaxed text-neutral-300">
              Compares where a driver started to where they finished. A driver who gained places wins against
              every classified finisher they passed; a driver who lost places loses to every classified
              finisher who passed them. A pit-lane start (grid = 0) is treated as starting behind the whole
              field, so it can only ever be a gain. Because one race can involve several opponents at once
              (unlike categories 1 and 3, which are always exactly one win plus one loss), this category runs
              at half weight so a single chaotic race can't swing a rating as much as qualifying or the finish
              order can.
            </p>
            <p class="mt-2 max-w-3xl text-sm leading-relaxed text-neutral-300">
              <strong class="text-neutral-100">On the K value:</strong> compared against categories 1 or 3
              individually, this category's typical per-race swing looked roughly double theirs — an early
              signal it might be overweighted. But categories 1 and 3 both measure the same thing (placement),
              while this one measures something different (race-craft: overtakes actually completed) — the
              fairer comparison is against categories 1 and 3 <em>combined</em>. Measured that way, this
              category's average magnitude over the last 10 seasons is only about 14% higher than theirs
              combined — close to balanced. Halving K further undershoots that balance instead, making
              race-craft count for less than placement as a whole rather than roughly the same.
            </p>
            <div class="mt-3 rounded-md border border-neutral-800 bg-neutral-950 p-4 text-sm text-neutral-400">
              <p class="font-semibold text-neutral-100">Example</p>
              <p class="mt-1">
                Started P8, finished P5 (rated 1000): passed the drivers who finished P6, P7 and P8 (rated
                1050, 950 and 1000).
              </p>
              <p class="mt-2 text-neutral-300">
                vs P6: <Katex expr="\Delta = 16(1 - 0.429) \approx" />
                <span class="text-emerald-400"><Katex expr="+9" /></span>
              </p>
              <p class="mt-2 text-neutral-300">
                vs P7: <Katex expr="\Delta = 16(1 - 0.571) \approx" />
                <span class="text-emerald-400"><Katex expr="+7" /></span>
              </p>
              <p class="mt-2 text-neutral-300">
                vs P8: <Katex expr="\Delta = 16(1 - 0.5) =" />
                <span class="text-emerald-400"><Katex expr="+8" /></span>
              </p>
              <p class="mt-2">
                net <span class="text-emerald-400">+24</span> for the recovery drive.
              </p>
            </div>
          </div>

          <div class="border-t border-neutral-800 pt-6">
            <div class="flex flex-wrap items-baseline justify-between gap-2">
              <h3 class="font-semibold text-neutral-100">3 · Race finishing position</h3>
              <span class="text-xs font-semibold tracking-widest text-neutral-500 uppercase">K = 32</span>
            </div>
            <p class="mt-2 max-w-3xl text-sm leading-relaxed text-neutral-300">
              Same one-above / one-below structure as qualifying, but on the final classified order. A driver
              who did not finish (retirement, mechanical failure, accident) gets a delta of 0 here — they're
              removed from the comparison entirely rather than penalised for it.
            </p>
            <div class="mt-3 rounded-md border border-neutral-800 bg-neutral-950 p-4 text-sm text-neutral-400">
              <p class="font-semibold text-neutral-100">Example</p>
              <p class="mt-1">
                Finished P4 (rated 1000), beating P5 (rated 900) but losing out to P3 (rated 1150):
              </p>
              <p class="mt-2 text-neutral-300">
                beats P5: <Katex expr="\Delta = 32(1 - 0.640) \approx" />
                <span class="text-emerald-400"><Katex expr="+12" /></span>
              </p>
              <p class="mt-2 text-neutral-300">
                loses to P3: <Katex expr="\Delta = 32(0 - 0.297) \approx" />
                <span class="text-red-400"><Katex expr="-10" /></span>
              </p>
              <p class="mt-2">
                net <span class="text-emerald-400">+2</span> — a routine, roughly-as-expected result barely
                moves the needle either way.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section id="special-cases" class="scroll-mt-6 rounded-lg border border-neutral-800 bg-neutral-900 p-8">
        <h2 class="text-lg font-bold">Special cases</h2>
        <dl class="mt-4 space-y-4 text-sm">
          <div>
            <dt class="font-semibold text-neutral-100">Retirement / DNS</dt>
            <dd class="mt-1 max-w-3xl text-neutral-300">
              Categories 2 and 3 are zeroed out, and the driver is removed from every other driver's win/loss
              pool for those categories too — nobody gains rating for "beating" a car that broke down. Category
              1 (qualifying) is unaffected, since it's decided before the race starts.
            </dd>
          </div>
          <div>
            <dt class="font-semibold text-neutral-100">Classified despite retiring (the "90%" rule)</dt>
            <dd class="mt-1 max-w-3xl text-neutral-300">
              F1's sporting regulations let a car that breaks down or otherwise fails to finish under power
              still be officially classified as a finisher, as long as it covered a high enough fraction of the
              race distance (colloquially "the 90% rule"). This project's retired-vs-classified split comes
              straight from that official classification (<code class="text-neutral-100">positionText</code>),
              not from whether the car crossed the line under its own power — so a car that broke down but
              stayed classified is still scored normally for categories 2 and 3, unlike a normal retirement.
              That's exactly what produced a notable upset at the 2026 Spanish Grand Prix
              (Barcelona-Catalunya): a late mechanical failure didn't zero out the driver's result the way an
              earlier DNF would have.
            </dd>
          </div>
          <div>
            <dt class="font-semibold text-neutral-100">Disqualification</dt>
            <dd class="mt-1 max-w-3xl text-neutral-300">
              Treated as a loss-only result: a DQ'd driver loses rating against the last classified finisher in
              category 3, can only lose (never gain) in category 2, and scores 0 for qualifying. Every other
              driver's win/loss pool excludes them entirely — nobody gains rating from a disqualification, and
              nobody loses to one.
            </dd>
          </div>
          <div>
            <dt class="font-semibold text-neutral-100">Pit-lane start</dt>
            <dd class="mt-1 max-w-3xl text-neutral-300">
              A grid position of 0 is normalised to the back of the field for category 2, so a pit-lane start
              can only ever gain rating, never lose it for the starting position itself.
            </dd>
          </div>
          <div>
            <dt class="font-semibold text-neutral-100">Rating floor</dt>
            <dd class="mt-1 max-w-3xl text-neutral-300">
              Ratings are floored at 100 — a run of bad results can't push a driver's rating below that, no
              matter how long the losing streak.
            </dd>
          </div>
        </dl>
      </section>

      <section id="interpreting-ratings" class="scroll-mt-6 rounded-lg border border-neutral-800 bg-neutral-900 p-8">
        <h2 class="text-lg font-bold">Interpreting the ratings</h2>
        <p class="mt-3 max-w-3xl text-sm leading-relaxed text-neutral-300">
          A single race's rating change is <em>volatile</em>, not a verdict. Category 2 alone can swing a
          double-digit amount from one chaotic, safety-car-affected race — a big recovery drive or a single bad
          qualifying upset can move a rating by more in one afternoon than a whole quiet season does. Special
          cases like the 90% rule above can also make one race behave very differently from what the raw
          result suggests.
        </p>
        <p class="mt-3 max-w-3xl text-sm leading-relaxed text-neutral-300">
          Treat the number after any one Grand Prix as a data point, not a conclusion. The rating is meant to
          be read as a <em>trajectory</em> — the shape of a driver's line across a season or a career on their
          <RouterLink :to="{ name: 'drivers-list' }" class="text-neutral-100 underline decoration-neutral-700 underline-offset-2 hover:text-white">
            driver page
          </RouterLink>
          — rather than any single race in isolation. Comparisons are also only meaningful across a similar
          span of races: different eras carry different average ratings in the pool, so a handful of races
          from two different decades don't compare cleanly against each other.
        </p>
      </section>

      <section id="scope-data" class="scroll-mt-6 rounded-lg border border-neutral-800 bg-neutral-900 p-8">
        <h2 class="text-lg font-bold">Scope &amp; data</h2>
        <p class="mt-3 max-w-3xl text-sm leading-relaxed text-neutral-300">
          Coverage starts in 1970, once every entry is a single chassis driven by a single named driver — before
          that, a single car could be shared between multiple drivers across a season, which the one-driver,
          one-rating model can't represent.
        </p>
        <ul class="mt-4 space-y-1.5 text-sm text-neutral-400">
          <li>
            jtrotman,
            <a
              href="https://www.kaggle.com/datasets/jtrotman/formula-1-race-data"
              target="_blank"
              rel="noopener noreferrer"
              class="text-neutral-300 underline decoration-neutral-700 underline-offset-2 hover:text-white"
              >Formula 1 World Championship (1950–2024)</a
            >, Kaggle.
          </li>
        </ul>
      </section>
      </div>
    </div>
  </section>
</template>
