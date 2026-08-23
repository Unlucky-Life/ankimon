package main

import (
	"errors"
	"math/rand"
	"sync"
	"time"
)

var (
	ErrRaidNotFound     = errors.New("raid not found")
	ErrRaidAlreadyOver  = errors.New("raid boss already defeated")
	ErrParticipantEmpty = errors.New("username is required")
)

// Participant tracks one trainer's contribution to a raid.
type Participant struct {
	Username    string    `json:"username"`
	DamageDealt int       `json:"damage_dealt"`
	JoinedAt    time.Time `json:"joined_at"`
}

// Raid is a shared boss fight. All mutation goes through Store's methods,
// which hold Store.mu for the duration - Raid itself has no independent lock.
type Raid struct {
	ID           string                  `json:"id"`
	BossName     string                  `json:"boss_name"`
	BossLevel    int                     `json:"boss_level"`
	MaxHP        int                     `json:"max_hp"`
	HP           int                     `json:"hp"`
	CreatedAt    time.Time               `json:"created_at"`
	Participants map[string]*Participant `json:"participants"`
}

func (r *Raid) IsDefeated() bool {
	return r.HP <= 0
}

// Store holds all active raids in memory, guarded by a single RWMutex.
// Good enough for the expected scale (a handful of concurrent raids with a
// few dozen participants each) - not intended to survive a process restart.
type Store struct {
	mu    sync.RWMutex
	raids map[string]*Raid
}

func NewStore() *Store {
	return &Store{raids: make(map[string]*Raid)}
}

func newRaidID() string {
	const alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789" // no 0/O/1/I to avoid confusion when shared verbally
	b := make([]byte, 6)
	for i := range b {
		b[i] = alphabet[rand.Intn(len(alphabet))]
	}
	return string(b)
}

func (s *Store) CreateRaid(bossName string, bossLevel, maxHP int) *Raid {
	s.mu.Lock()
	defer s.mu.Unlock()

	if maxHP <= 0 {
		maxHP = 1
	}

	var id string
	for {
		id = newRaidID()
		if _, exists := s.raids[id]; !exists {
			break
		}
	}

	raid := &Raid{
		ID:           id,
		BossName:     bossName,
		BossLevel:    bossLevel,
		MaxHP:        maxHP,
		HP:           maxHP,
		CreatedAt:    time.Now(),
		Participants: make(map[string]*Participant),
	}
	s.raids[id] = raid
	return raid
}

// ListActive returns all raids whose boss hasn't been defeated yet.
func (s *Store) ListActive() []*Raid {
	s.mu.RLock()
	defer s.mu.RUnlock()

	active := make([]*Raid, 0, len(s.raids))
	for _, r := range s.raids {
		if !r.IsDefeated() {
			active = append(active, r)
		}
	}
	return active
}

func (s *Store) Get(id string) (*Raid, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	raid, ok := s.raids[id]
	if !ok {
		return nil, ErrRaidNotFound
	}
	return raid, nil
}

func (s *Store) Join(id, username string) (*Raid, error) {
	if username == "" {
		return nil, ErrParticipantEmpty
	}

	s.mu.Lock()
	defer s.mu.Unlock()

	raid, ok := s.raids[id]
	if !ok {
		return nil, ErrRaidNotFound
	}
	if _, already := raid.Participants[username]; !already {
		raid.Participants[username] = &Participant{
			Username: username,
			JoinedAt: time.Now(),
		}
	}
	return raid, nil
}

// Attack applies clamped damage from one participant's move to the raid boss.
// See maxPossibleDamage for why the claimed damage is clamped rather than
// trusted outright.
func (s *Store) Attack(id, username string, claimedDamage int, level, basePower, atkStat, defStat int) (*Raid, int, error) {
	if username == "" {
		return nil, 0, ErrParticipantEmpty
	}

	s.mu.Lock()
	defer s.mu.Unlock()

	raid, ok := s.raids[id]
	if !ok {
		return nil, 0, ErrRaidNotFound
	}
	if raid.IsDefeated() {
		return nil, 0, ErrRaidAlreadyOver
	}

	participant, joined := raid.Participants[username]
	if !joined {
		participant = &Participant{Username: username, JoinedAt: time.Now()}
		raid.Participants[username] = participant
	}

	dmg := clampDamage(claimedDamage, level, basePower, atkStat, defStat)

	raid.HP -= dmg
	if raid.HP < 0 {
		raid.HP = 0
	}
	participant.DamageDealt += dmg

	return raid, dmg, nil
}
