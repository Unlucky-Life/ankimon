package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
	"strings"
)

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
// X-Ankimon-Username / X-Ankimon-Api-Key headers. There's no account system
// behind this yet (v1 matches the addon's existing leaderboard feature,
// which is also just "well-formed credentials", not a verified identity) -
// this exists to keep accidental/anonymous traffic out, not to authenticate.
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
		next.ServeHTTP(w, r)
	})
}

func writeJSON(w http.ResponseWriter, status int, body interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(body)
}
