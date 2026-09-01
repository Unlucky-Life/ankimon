package main

import (
	"encoding/json"
	"net/http"
)

func registerRoutes(mux *http.ServeMux, store *Store) {
	mux.HandleFunc("GET /healthz", func(w http.ResponseWriter, r *http.Request) {
		writeJSON(w, http.StatusOK, map[string]string{"status": "ok"})
	})

	mux.HandleFunc("POST /raids", createRaidHandler(store))
	mux.HandleFunc("GET /raids", listRaidsHandler(store))
	mux.HandleFunc("GET /raids/{id}", getRaidHandler(store))
	mux.HandleFunc("POST /raids/{id}/join", joinRaidHandler(store))
	mux.HandleFunc("POST /raids/{id}/attack", attackRaidHandler(store))
}

type createRaidRequest struct {
	BossName  string `json:"boss_name"`
	BossLevel int    `json:"boss_level"`
	MaxHP     int    `json:"max_hp"`
}

func createRaidHandler(store *Store) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		var req createRaidRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid JSON body"})
			return
		}
		if req.BossName == "" {
			writeJSON(w, http.StatusBadRequest, map[string]string{"error": "boss_name is required"})
			return
		}
		raid := store.CreateRaid(req.BossName, req.BossLevel, req.MaxHP)
		writeJSON(w, http.StatusCreated, raid)
	}
}

func listRaidsHandler(store *Store) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		writeJSON(w, http.StatusOK, store.ListActive())
	}
}

func getRaidHandler(store *Store) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		raid, err := store.Get(r.PathValue("id"))
		if err != nil {
			writeJSON(w, http.StatusNotFound, map[string]string{"error": err.Error()})
			return
		}
		writeJSON(w, http.StatusOK, raid)
	}
}

// joinRaidHandler and attackRaidHandler intentionally do NOT accept a
// "username" field in the request body - the participant identity always
// comes from the authenticated X-Ankimon-Username header (see
// authenticatedUsername/requireCredentials in main.go). Trusting a
// body-supplied username would let any authenticated caller act, join, or
// deal damage as anyone else.

func joinRaidHandler(store *Store) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		raid, err := store.Join(r.PathValue("id"), authenticatedUsername(r))
		if err != nil {
			writeJSON(w, statusForError(err), map[string]string{"error": err.Error()})
			return
		}
		writeJSON(w, http.StatusOK, raid)
	}
}

type attackRaidRequest struct {
	Damage    int `json:"damage"`     // damage the client computed locally
	Level     int `json:"level"`      // attacker's Pokemon level
	BasePower int `json:"base_power"` // move base power
	AtkStat   int `json:"atk_stat"`
	DefStat   int `json:"def_stat"`
}

type attackRaidResponse struct {
	Raid           *Raid `json:"raid"`
	DamageAccepted int   `json:"damage_accepted"`
}

func attackRaidHandler(store *Store) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		var req attackRaidRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid JSON body"})
			return
		}
		raid, accepted, err := store.Attack(r.PathValue("id"), authenticatedUsername(r), req.Damage, req.Level, req.BasePower, req.AtkStat, req.DefStat)
		if err != nil {
			writeJSON(w, statusForError(err), map[string]string{"error": err.Error()})
			return
		}
		writeJSON(w, http.StatusOK, attackRaidResponse{Raid: raid, DamageAccepted: accepted})
	}
}

func statusForError(err error) int {
	switch err {
	case ErrRaidNotFound:
		return http.StatusNotFound
	case ErrRaidAlreadyOver:
		return http.StatusConflict
	case ErrParticipantEmpty:
		return http.StatusBadRequest
	default:
		return http.StatusInternalServerError
	}
}
