# User guide

Everything on the screen, what it means, and what to do when you see a message. For how a dispatch team can use the app day to day, see [operations.md](operations.md).

## Contents

1. [Before you start](#1-before-you-start)
2. [The screen](#2-the-screen)
3. [Planning a trip](#3-planning-a-trip)
4. [Reading the result](#4-reading-the-result)
5. [Risk levels](#5-risk-levels)
6. [Moving through time](#6-moving-through-time)
7. [Changing the trip](#7-changing-the-trip)
8. [Messages and what to do](#8-messages-and-what-to-do)
9. [Questions](#9-questions)

## 1. Before you start

- Any current browser on a computer, tablet or phone.
- Trips must start and end in the **US, Canada or Mexico**, on roads that connect.
- Departure can be **from now up to 5 days ahead**, so the whole trip stays inside the weather forecast.
- Times are shown in **your device's time zone**.

## 2. The screen

On a computer or wide tablet:

| Area | Where | What it shows |
|---|---|---|
| **Map** | Left, about 70% of the screen | The three routes, checkpoints, the weather layer and the trucks |
| **Trip** | Top right | The form, or a one-line summary of the trip with a **Change trip** button |
| **Verdict** | Under the trip | Which route to take, its arrival time, the serious weather on it, and why it won |
| **Schedule** | Right, below the verdict | One lane per route, with time running downward, and the playhead |
| **Legend** | Bottom right | The five risk colours |

On a phone, the same parts stack in this order: trip, map, verdict, schedule.

## 3. Planning a trip

| Field | What to enter | Tips |
|---|---|---|
| **From**, **To** | A city or address | Pick a suggestion for an exact place, or type freely and the server finds it. |
| **Departure** | Date and time | Use the real planned departure. Weather is read at the hour the truck reaches each checkpoint, so time matters as much as place. |
| **Load (pounds)** | Weight of the load, up to 80,000 | Heavy loads make strong wind more dangerous (see [Risk levels](#5-risk-levels)). |
| **Check the weather every** | 10, 25 or 50 miles | **10 miles:** mountains, coasts, or when storms are forecast. **25 miles:** routine trips. **50 miles:** a quick look at a long haul. |

Press **Compare routes**. A short trip takes a few seconds; a coast-to-coast trip about 10 seconds. The same trip again within 30 minutes is almost instant.

## 4. Reading the result

### The verdict

For example: *"Take I 45. Arrive Sun 8:12 AM. No High or Severe weather on the way."* The second line gives the reason, for example *"Same weather risk as the alternatives, and 1.5 hours faster than the next best route."* A yellow notice appears if every route crosses No Travel conditions, or if part of a trip is beyond the forecast.

### The map

- **Route lines.** The selected route is blue and drawn on top; the others are grey. Click a line to select that route. Each route is labelled with its main highways and drive time.
- **Checkpoints.** Coloured dots at every check, coloured by risk level. The selected route's dots are larger.
- **Checkpoint details.** Click a dot to see how far it is from the start, when the truck gets there, the overall level, and wind (mph, miles per hour), rain and snow (in/hr, inches per hour), each with its level. Hover a unit to see it spelled out. If the load made the wind level worse, it says so, for example *"Wind level raised because the load is 40,000 pounds."*
- **Start and end.** A hollow ring marks the start; a filled dot marks the end.
- **Trucks.** One truck per route shows where it is at the playhead's time. The selected route's truck is blue. Hover a truck to see its mile, or "Not left yet" or "Arrived".

### The schedule

- **Lanes.** One per route, ordered by rank. The header shows the route's highways, drive time, distance, and any High, Severe or No Travel miles. **Best** marks the recommendation.
- **Colours.** Each lane is coloured by the risk the truck meets at each hour, from departure at the top to arrival at the bottom.
- **Arrival.** A tag at the end of each lane shows the arrival time.
- **Time axis.** On the left: 6 AM, 12 PM and 6 PM, with day names in bold at midnight.
- **Long trips.** When a trip lasts more than 48 hours, the schedule stretches to show the whole drive. A dashed line marks 48 hours, and the part after it is shaded: those colours are still real forecasts, but the playhead, trucks and weather layer stop at 48 hours.

## 5. Risk levels

Each checkpoint takes the **worst** of its wind, rain and snow levels.

| Level | Colour | Wind (mph) | Rain (in/hr) | Snow (in/hr) |
|---|---|---|---|---|
| Low | Green | under 25 | under 0.10 | under 0.5 |
| Moderate | Yellow | 25 to 34 | 0.10 to under 0.25 | 0.5 to under 1.0 |
| High | Orange | 35 to 44 | 0.25 to under 0.50 | 1.0 to under 2.0 |
| Severe | Red | 45 to 54 | 0.50 to 1.00 | 2.0 to 3.0 |
| No Travel | Dark red | 55 or more | over 1.00 | over 3.0 |

**Heavy loads and wind:**

- 45 to 54 mph wind with a load **over 30,000 lb** is **No Travel**.
- 35 to 44 mph wind with a load **over 40,000 lb** is **Severe**.
- 55 mph or more is No Travel for any load.

How the table's shared edges are read (for example, why exactly 0.25 in/hr of rain is High) is explained in [decisions.md](decisions.md#adr-007-reading-the-risk-table).

## 6. Moving through time

- **Drag the forecast slider** under "Weather at" to move through the 48 hours.
- **Drag** anywhere in the schedule's lanes to move the playhead. The dark pill on the left shows its time.
- **Keyboard:** click the pill (or Tab to it), then use **Up** and **Down** for 1 hour, **Page Up** and **Page Down** for 6 hours, and **Home** and **End** for departure and 48 hours.
- **Weather layer.** The coloured haze on the map is the risk along the corridor at the playhead's time. Use the **Weather layer** checkbox to hide or show it.
- **Hover a lane** to circle that checkpoint on the map.

## 7. Changing the trip

- **Select a route:** click its line on the map, its lane header, or anywhere in its lane.
- **Change the trip or check another place:** press **Change trip**, or click the trip summary. The form opens with the current trip filled in; change any field (use the × in From or To to start a new place) and press **Compare routes**. **Cancel** goes back to the current results and drops the changes.
- **Try another departure time:** a quick way to see whether waiting a few hours avoids a storm. Change only the departure and compare again.

## 8. Messages and what to do

| Message | Meaning | What to do |
|---|---|---|
| Enter where the trip starts / ends. | From or To is empty | Enter a place. |
| Pick a date and time. | Departure is empty | Choose a date and time. |
| Departure is in the past. | Departure is more than an hour ago | Choose a later time. |
| Forecasts only reach 5 days ahead. | Departure is too far away | Choose a departure within 5 days. |
| Enter a weight. / Use 80,000 lb or less. | Weight is missing or too high | Enter the load in pounds. |
| This planner covers the US, Canada and Mexico. | A place is outside the service area | Choose a place in North America. |
| No place called "..." in the US, Canada and Mexico. | The typed place was not found | Check the spelling, or pick a suggestion. |
| No road connects these two places. | For example, Hawaii to the mainland | Choose places on the same road network. |
| One of the places is too far from a road. | The point is in open country or water | Choose a nearby town or address. |
| ... is busy (rate limit). Try again in a minute. | A free data service is at its limit | Wait a minute and press **Compare routes** again. |
| Could not reach the server. | Network problem | Check the connection and try again. |
| Every route crosses No Travel conditions. Consider a later departure. | No safe route at this time | Try a later departure (see [operations.md](operations.md#4-decide)). |
| Part of the trip is beyond the weather forecast. | The trip ends after the forecast does | Those miles are not rated. Plan closer to departure. |

## 9. Questions

**Why are all the lanes green?** The weather along those routes is calm at those hours. Try a trip through an area with a storm in the news to see other colours.

**Why is a slower route recommended?** Safety comes first: the app ranks by Severe (or worse) miles, then High miles, then average risk, before time. The verdict's second line names the deciding rule.

**Why does a US trip pass through Canada?** The free routing service plans for cars and does not avoid borders. Check border crossings separately (see the README's known limitations).

**Why does the slider stop at 48 hours?** The weather layer and moving trucks cover the brief's 48-hour window. Lanes still show forecast risk past 48 hours on long trips.

**Why do times differ from the truck's local time?** All times are in your device's time zone.
