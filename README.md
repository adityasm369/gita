# Bhagavad Gita — Inner-Science Dashboard

A single self-contained HTML file: all 701 shlokas in Sanskrit, IAST, Telugu
script, Telugu bhavam and two English translations, plus per-chapter commentary
through six lenses, search and filters, statistics charts, and a quiz.

**Live, behind a login:**
`https://openclaw-87fc.srv1564960.hstgr.cloud/assets/gita.html`

Username is the email address; the password lives in `/docker/gita/.password`
on the host (mode 600).

## How it is served

Unlike the game-for-it dashboard, this one is **not** symlinked into the
OpenClaw wrapper's `/assets` directory. That route is deliberately mounted
*before* the wrapper's auth middleware:

```js
d.use("/assets", C.static("./src/views/assets"));   // no auth, by design
d.use(V, proxy(...));                               // V = auth, proxies to openclaw
```

so anything placed there is public, and every other path proxies to the openclaw
gateway rather than serving files. There is no way to get authentication on a
static file from inside the wrapper.

Instead the auth sits in front, in Traefik:

```
Traefik (host network, :443, existing LE cert)
  ├── Host(...) && Path(`/assets/gita.html`)   priority 100  → basicauth → gita-gita-1 (nginx)
  └── Host(...)                                              → openclaw-87fc-openclaw-1
```

The compose project is on the host at **`/docker/gita/`**. The router rule is
strictly more specific than openclaw's Host-only rule and pinned to priority
100, so it wins for this one path and changes nothing else on the host.

nginx bind-mounts *this* `dashboard.html` read-only, so it stays the single
source of truth — editing it is live immediately, no rebuild, no relink. The
container restarts with Docker and survives an openclaw rebuild, because it is
a separate compose project.

```sh
cd /docker/gita && docker compose up -d      # start / apply label changes
docker compose logs -f                       # nginx access log
```

## Changing the password

```sh
NEW='pick-something-long'
openssl passwd -apr1 "$NEW"                  # copy the hash
# put it in /docker/gita/docker-compose.yml on the basicauth.users label,
# doubling every $ to $$, then:
cd /docker/gita && docker compose up -d
```

## Known limitation

Basic auth has no session, no logout, and **no password reset flow** — the
browser caches the credentials until it is restarted. Moving to a real portal
(Authelia with emailed reset links, or Google sign-in via oauth2-proxy) is a
drop-in replacement: same router, swap the `basicauth` middleware for
`forwardAuth`.

```
dashboard.html        the deliverable — single file, open it directly
README.md             this file
/docker/gita/         the compose project that serves it (on the host)
```

## Source

Built from `/root/gita/bhagavad_gita_dashboard.html` on the host. That file is
the original; this copy adds five deployment fixes and is the one served:

- **Theme** — the original only handled an explicit `[data-theme="dark"]`
  toggle, so a visitor whose OS is dark but who never touched the button got
  light tokens. A `prefers-color-scheme` block now covers that state, guarded so
  an explicit light choice still wins, and the 🌙/☀️ button reads the resolved
  theme at boot instead of assuming light.
- **Overflow** — the three Inner-Science tables scroll inside their own
  containers rather than pushing the page sideways on a phone.
- **Speech** — `speechSynthesis` ran at top level and would take the whole boot
  sequence down where the API is unavailable. Now guarded; the 🔊 buttons no-op
  instead.
- **Accessibility** — visible keyboard focus rings, `prefers-reduced-motion`.

## Data

701 verses (700 in the standard Vulgate; ch.13 carries one extra opening
question in this recension). Per-chapter counts match the canonical text.
Sanskrit, IAST and word-by-word meanings come from the open `gita/gita` dataset;
English is Swami Sivananda (primary) and Shri Purohit Swami (alternate); the
Telugu script is transliterated from Devanagari and the bhavam is a fresh
concise rendering. The NLP, chakra and psychology lenses are a contemplative
mapping offered as study aids, not scriptural claims — as the footer states.
