# Architecture decision records

One record per significant choice: the context, the decision, the alternatives considered, and the consequences. All records are accepted unless marked otherwise.

| # | Decision |
|---|---|
| [001](#adr-001-modular-monolith) | Modular monolith |
| [002](#adr-002-no-database) | No database |
| [003](#adr-003-free-keyless-providers-behind-adapters) | Free, keyless providers behind adapters |
| [004](#adr-004-three-routes-from-alternatives-plus-detours) | Three routes from alternatives plus detours |
| [005](#adr-005-truck-drive-time) | Truck drive time |
| [006](#adr-006-checkpoints-and-the-miles-they-cover) | Checkpoints and the miles they cover |
| [007](#adr-007-reading-the-risk-table) | Reading the risk table |
| [008](#adr-008-which-forecast-hour-a-checkpoint-reads) | Which forecast hour a checkpoint reads |
| [009](#adr-009-ranking-order) | Ranking order |
| [010](#adr-010-a-location-budget-per-plan) | A location budget per plan |
| [011](#adr-011-heatmap-as-hourly-image-frames) | Heatmap as hourly image frames |
| [012](#adr-012-map-plus-vertical-schedule) | Map plus vertical schedule |
| [013](#adr-013-service-area-and-error-codes) | Service area and error codes |
| [014](#adr-014-a-muted-base-map) | A muted base map |

## ADR-001: Modular monolith

**Context.** A 16-hour build that must be easy to run, review and deploy, yet clearly structured.

**Decision.** One Django service and one React app, each split by capability (`routing`, `weather`, `risk`, `planner`, `api`; and `trip-form`, `map`, `timeline`, `forecast`). Dependencies point one way, and features never import each other.

**Alternatives.** Microservices (extra deployment and network failure modes with no benefit at this size); a flat app with logic in views (fast to write, hard to test and change).

**Consequences.** One deploy per tier. Each module can be tested alone, and any module can become a service later without rewriting its logic.

## ADR-002: No database

**Context.** The brief has no stored entities: every plan is computed from live routing and weather data.

**Decision.** No database. Repeated lookups are cached in memory for 30 minutes (24 hours for place search).

**Alternatives.** PostgreSQL for saved trips or share links (an extra feature the brief does not ask for); SQLite (unused weight).

**Consequences.** Nothing to migrate or back up. The cache is per process; with several processes, switch `CACHES` to Redis, a one-setting change.

## ADR-003: Free, keyless providers behind adapters

**Context.** The brief allows third-party APIs. Reviewers should be able to run the app without creating accounts.

**Decision.** Photon for place search, the public OSRM server for routing, and Open-Meteo for forecasts. Each sits behind one module, and each base URL is configurable.

**Alternatives.** Google Maps, HERE or Mapbox (better data, including truck profiles, but they need keys and billing); the National Weather Service API (US only, one request per point, slower).

**Consequences.** Zero setup. In exchange: car-only routing, fair-use rate limits, and attribution requirements, which the map credits line satisfies. All of these are listed in the README's limitations, with fixes.

## ADR-004: Three routes from alternatives plus detours

**Context.** OSRM often returns only one or two alternatives. For Dallas to Houston it returned one.

**Decision.** Fill the gap with detour routes through side waypoints at 8, 15, 30 and 45 percent of the trip length on both sides of the midpoint. Keep candidates no slower than 2.5 times the fastest route that share less than 80 percent of their road with every kept route. Take the fastest survivors.

**Alternatives.** Showing fewer than three routes (fails the brief); random waypoints (unpredictable, unstable between runs).

**Consequences.** Three distinct routes on every trip tested, including mountain and coastal corridors. Detours are real roads but can be longer than a dispatcher's own alternatives. The overlap rule also rejects the out-and-back spurs a waypoint on a dead-end road creates.

## ADR-005: Truck drive time

**Context.** OSRM's times are for cars.

**Decision.** Cap each road segment at 65 mph (configurable with `TRUCK_MAX_MPH`), and use the capped time for both ETAs and the route's travel time, so they always agree.

**Alternatives.** A fixed percentage slowdown (wrong on slow roads, where cars and trucks travel at similar speeds); hours-of-service breaks (more realistic, but an extra feature).

**Consequences.** Reasonable ETAs for daytime trips. Long trips ignore the mandatory 30-minute and 10-hour breaks; this is listed as a known limitation.

## ADR-006: Checkpoints and the miles they cover

**Context.** The ranking is about "Severe miles" and "High miles", but weather is sampled at points.

**Decision.** Place checkpoints along the road (not in a straight line) at mile 0, every N miles, and at the destination. Each checkpoint covers half the distance to each neighbour, so coverage sums to exactly the trip length.

**Alternatives.** Each checkpoint covering the segment ahead (biases toward the start); counting checkpoints instead of miles (unfair across 10, 25 and 50-mile spacing).

**Consequences.** Mileage is comparable across routes and spacings, and is directly testable (coverage equals trip length).

## ADR-007: Reading the risk table

**Context.** The brief's table overlaps at its edges: rain of 0.25 in/hr appears in both "0.10 to 0.25" (Moderate) and "0.25 to 0.50" (High).

**Decision.**
- Each band includes its lower bound, so 25 mph is Moderate, 0.25 in/hr of rain is High, and 0.50 in/hr is Severe. When a value sits on an overlap, the safer reading wins.
- "No Travel" uses the brief's own symbols: wind at or above 55 mph; rain above 1.00 in/hr; snow above 3.0 in/hr. So exactly 1.00 in/hr of rain is Severe.
- The load rules only raise the wind level, never lower it. "Above 30,000 lb" is strict, so exactly 30,000 lb does not trigger it.
- A checkpoint's level is the worst of wind (after the load rule), rain and snow.

**Alternatives.** Upper-bound inclusive (puts a value on an overlap in the milder band); adding the three conditions together (not in the brief).

**Consequences.** Every boundary is unambiguous and has a test.

## ADR-008: Which forecast hour a checkpoint reads

**Context.** Forecasts are hourly; trucks arrive at arbitrary minutes. Open-Meteo stamps rain and snow totals at the end of each hour.

**Decision.** Wind is interpolated between the two surrounding hours. Rain and snow use the hour being driven through: a truck at 1:30 reads the value stamped 2:00. Rain includes showers.

**Alternatives.** Nearest hour for everything (reads the previous hour's rain half of the time).

**Consequences.** Precipitation matches the hour the truck is actually in. The rule has its own tests.

## ADR-009: Ranking order

**Context.** The brief's order is fewest Severe miles, fewest High miles, lowest average risk, then shortest time. It does not mention No Travel.

**Decision.** Compare No Travel miles first, then follow the brief's order. Average risk is weighted by miles. Values are rounded (0.1 mile, 0.01 risk) before comparing. The response explains the decision by naming the first rule that separated the winner from the runner-up.

**Alternatives.** A weighted score blending risk and time (hides the brief's priorities, and is hard to explain).

**Consequences.** A route that crosses No Travel conditions never wins over one that doesn't, and every recommendation can be explained in one sentence.

## ADR-010: A location budget per plan

**Context.** Testing a coast-to-coast trip at 10-mile spacing requested more than 600 weather locations and hit Open-Meteo's free limit (HTTP 429).

**Decision.** Hold each plan to about 300 locations: checkpoints use at most 200 grid cells, with the grid coarsening from 0.1 to 1.0 degrees only when needed; the heatmap uses at most 100 cells. Busy responses are retried after 1 and 3 seconds, then reported plainly.

**Alternatives.** One request per checkpoint (slow and hits the limit sooner); a paid plan (removes the limit, but adds setup for reviewers).

**Consequences.** Short and medium trips keep a fine grid (about 7 miles). Very long trips share weather cells between nearby checkpoints, while each checkpoint still reads the forecast at its own ETA.

## ADR-011: Heatmap as hourly image frames

**Context.** The slider must feel instant (UI and performance are 40 percent of the grade), and the heatmap shows a value per area, not a density of points.

**Decision.** The server returns one row of 0 to 4 intensities per hour. The browser turns each hour into a tiny image (one pixel per cell) once, and the map stretches it smoothly over the corridor. Moving the slider swaps images.

**Alternatives.** `leaflet.heat` (a density heatmap: overlapping points add up, so calm areas look stormy); drawing rectangles per cell (blocky, and many more elements).

**Consequences.** No network calls and no recalculation while scrubbing. Colours match the checkpoint colours exactly. On very tall corridors, the simple image stretch shifts cells slightly in latitude, which is acceptable for a visual layer.

## ADR-012: Map plus vertical schedule

**Context.** Early layouts were a form sidebar with a map (common in similar tools), floating panels over the map (they hid routes), and stacked bands above and below the map (they squeezed it).

**Decision.** The map takes about 70 percent of the width with nothing covering it. The right column holds the trip, the verdict and a schedule where time runs downward, with one lane per route coloured by the risk met at each hour. One playhead drives the trucks and the weather layer.

**Alternatives.** The layouts above, and a full-screen map with small floating tools.

**Consequences.** Routes are compared by time, the dimension that matters for weather. The playhead is a keyboard-accessible slider. On phones, the column stacks under the map.

## ADR-013: Service area and error codes

**Context.** A trip from Davao City to Arizona reached the router and failed with a raw provider error.

**Decision.** Place search and validation are limited to North America (the US, Canada and Mexico), one connected road network. Places outside it are field errors (400). "No road connects these places", for example Hawaii to Arizona, returns 422, because the input is the problem, not the server. Provider failures return 502. Messages never include request URLs. A failed search clears the previous result on screen.

**Alternatives.** Worldwide search (most trips would be impossible); returning every failure as 502 (misleads clients about whose fault it is).

**Consequences.** Impossible trips fail fast with a clear message. Restricting to the US only needs a country check instead of a bounding box; this is an open question.

## ADR-014: A muted base map

**Context.** The standard OpenStreetMap style uses orange highways and green parks, which compete with the risk colours. Free muted styles now require API keys.

**Decision.** Use standard OpenStreetMap tiles with a CSS filter at 50 percent greyscale. Roads, water and parks keep a hint of colour, and the data stays the most saturated thing on screen.

**Alternatives.** Full-colour tiles (colour clash); a keyed light style from MapTiler or Stadia (best look, but adds an account and key).

**Consequences.** No key needed. Heavy production use should move to a tile provider, since the public OpenStreetMap tile servers are meant for light use.
