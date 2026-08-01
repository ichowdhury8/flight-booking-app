# Demo video — shot list

**Target: under 2:30. No audio required.**

Destination is **Atlanta**, deliberately: it is the guide you can personally
vouch for, and an inbound transatlantic leg shows off the overnight arrival that
the seed-time offset arithmetic exists to get right.

---

## Before you hit record

- [ ] **Warm the instance.** Load the live URL a minute or two beforehand. A
      cold start on Render's free tier takes ~50 seconds and would open the
      video with a blank page.
- [ ] **Do not reuse an old booking reference.** The database is reseeded on
      every cold start, so any reference from a previous session has already
      stopped resolving. Book fresh, on camera.
- [ ] Set a fixed, tidy window size — around 1280×800. Avoid full screen on a
      large display; the layout is capped at 1120px and you will film a lot of
      background.
- [ ] Close other tabs, hide bookmarks, clear notifications.
- [ ] Pick a date a few days out rather than today, so the itinerary reads
      naturally.
- [ ] `⌘⇧5` → Record Selected Portion.

---

## Seven beats

| # | Beat | Time | What matters |
|---|---|---|---|
| 1 | **Landing page** | 0:10 | Let it sit still for a beat. Serif hero, one accent colour, plenty of whitespace. Don't move the cursor. |
| 2 | **Search** | 0:20 | London (LHR) → Atlanta (ATL). Set passengers to 2 — it makes the price summary and the ticket list more interesting later. |
| 3 | **Results** | 0:15 | Pause here. Two flights, visibly different departure times, carriers and prices. This is the trade-off the seed was built to show — let it land before clicking. |
| 4 | **Select a flight** | 0:15 | Passenger page. The sticky sidebar shows the itinerary and running total. |
| 5 | **Fill details** | 0:30 | Type at a natural pace. Two passengers plus contact details. Don't rush it — this is the least interesting beat, but hurrying it looks like hiding something. |
| 6 | **Confirm** | 0:20 | The reference code, large and legible. Hold long enough to read it aloud. |
| 7 | **Arrival Guide** | 0:35 | **The differentiator — give it the most time.** Scroll down slowly. Rest on the transfer callout: MARTA, ~20 min, 10 mi. Then the four attractions. End here. |

---

## Optional eighth beat, if you're under time

Copy the confirmation URL, open it in a new tab, and let it load. It proves the
booking is real and server-backed rather than client state — the page refetches
by reference and renders identically. Costs about ten seconds.

---

## What to avoid

- **Don't demo the empty state or an error.** They exist and they work, but they
  aren't the story and they eat the clock.
- **Don't resize the window mid-take.** The layout is responsive, but a reflow
  on camera reads as instability.
- **Don't show `/docs`.** It's useful, and it's a different video.
- **Don't linger on the search form while nothing is happening.** Beat 2 should
  feel brisk; beats 3 and 7 are where the time belongs.

---

## If you need a second take

The seed is deterministic, so the same route on the same date returns the same
flights at the same prices every time. Only the booking reference changes
between takes — everything else you filmed will match.
