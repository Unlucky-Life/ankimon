# ankimon raid server

A small self-hostable relay server for Ankimon's raid feature: multiple
trainers fight a shared boss Pokemon together, dealing damage as they review
Anki cards. In-memory only (no database) - state resets on restart.

## Running it

```sh
go run .
# or
go build -o ankimon-raid-server .
./ankimon-raid-server
```

Listens on `:8080` by default; override with the `PORT` env var.

## API

Every request except `GET /healthz` requires two headers:

```
X-Ankimon-Username: <trainer name>
X-Ankimon-Api-Key: <any non-empty value>
```

There's no real account system yet (v1 matches the addon's leaderboard
feature, which is also "well-formed credentials", not verified identity) -
this exists to keep anonymous/accidental traffic out, not to authenticate.

| Method | Path                  | Body                                                                 | Notes |
|--------|-----------------------|-----------------------------------------------------------------------|-------|
| GET    | `/healthz`            | -                                                                     | no auth required |
| POST   | `/raids`               | `{"boss_name","boss_level","max_hp"}`                                 | creates a raid, returns it with a short `id` |
| GET    | `/raids`               | -                                                                     | lists raids whose boss hasn't been defeated yet |
| GET    | `/raids/{id}`          | -                                                                     | full raid state, including participants |
| POST   | `/raids/{id}/join`     | `{"username"}`                                                        | idempotent - joining twice is a no-op |
| POST   | `/raids/{id}/attack`   | `{"username","damage","level","base_power","atk_stat","def_stat"}`    | see below |

### Anti-cheat on `/attack`

The client computes its own damage locally (same formula the addon already
uses for solo battles) and submits it, along with the inputs that produced
it. The server independently computes a generous theoretical ceiling for
that same formula (`damage.go: maxPossibleDamage`) and clamps the claim to
it - so a modified client can't report arbitrary damage against the shared
boss. The response's `damage_accepted` field is the number actually applied;
compare it to what you sent if you need to detect clamping.

This is an approximation (no access to the addon's type effectiveness chart
server-side), tuned to always let legitimate hits through and only reject
physically-impossible claims - not a byte-for-byte reimplementation of the
Python damage formula.

## Manual smoke test

```sh
go run . &
curl -s http://localhost:8080/healthz

RAID=$(curl -s -X POST http://localhost:8080/raids \
  -H "X-Ankimon-Username: leon" -H "X-Ankimon-Api-Key: k" \
  -d '{"boss_name":"Rayquaza","boss_level":70,"max_hp":500}')
echo "$RAID"
# grab "id" from the response, then:
curl -s -X POST http://localhost:8080/raids/<id>/join \
  -H "X-Ankimon-Username: leon" -H "X-Ankimon-Api-Key: k" \
  -d '{"username":"leon"}'
curl -s -X POST http://localhost:8080/raids/<id>/attack \
  -H "X-Ankimon-Username: leon" -H "X-Ankimon-Api-Key: k" \
  -d '{"username":"leon","damage":25,"level":20,"base_power":40,"atk_stat":50,"def_stat":50}'
```

## Not implemented yet (v1 scope)

- Real-time push - clients poll `GET /raids/{id}`. A websocket upgrade is a
  natural v2 addition on top of the same `Store`.
- Persistence - an in-process restart drops all raid state.
- Deployment/hosting - this is just the server; where it runs is up to you
  (a `Dockerfile`/Fly.io/Render config can be added when you pick one).
