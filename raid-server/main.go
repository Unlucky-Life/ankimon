package main

import (
	"context"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"strings"
)

type contextKey string

const usernameContextKey contextKey = "ankimon-username"

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	store := NewStore()
	mux := http.NewServeMux()
	registerRoutes(mux, store)

	log.Printf("ankimon raid server listening on :%s", port)
	if err := http.ListenAndServe(":"+port, requireCredentials(mux)); err != nil {
		log.Fatal(err)
	}
}

// requireCredentials enforces that every request carries non-empty
// X-Ankimon-Username / X-Ankimon-Api-Key headers, and stashes the
// authenticated username in the request context so handlers use *that*
// identity - never a "username" field from the request body, which a
// client could set to impersonate someone else.
//
// There's no account system behind this yet (v1 matches the addon's
// existing leaderboard feature, which is also just "well-formed
// credentials", not a verified identity) - this exists to keep
// accidental/anonymous traffic out and to bind every action to the caller
// who authenticated it, not to cryptographically verify who they are.
func requireCredentials(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/healthz" {
			next.ServeHTTP(w, r)
			return
		}
		username := strings.TrimSpace(r.Header.Get("X-Ankimon-Username"))
		apiKey := strings.TrimSpace(r.Header.Get("X-Ankimon-Api-Key"))
		if username == "" || apiKey == "" {
			writeJSON(w, http.StatusUnauthorized, map[string]string{
				"error": "X-Ankimon-Username and X-Ankimon-Api-Key headers are required",
			})
			return
		}
		ctx := context.WithValue(r.Context(), usernameContextKey, username)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

func authenticatedUsername(r *http.Request) string {
	username, _ := r.Context().Value(usernameContextKey).(string)
	return username
}

func writeJSON(w http.ResponseWriter, status int, body interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(body)
}
