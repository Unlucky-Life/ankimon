package main

import (
	"sync"
	"testing"
)

func TestCreateRaidDefaultsAndGet(t *testing.T) {
	store := NewStore()
	raid := store.CreateRaid("Rayquaza", 70, 500)

	if raid.HP != 500 || raid.MaxHP != 500 {
		t.Fatalf("expected HP/MaxHP to start at 500, got HP=%d MaxHP=%d", raid.HP, raid.MaxHP)
	}
	if raid.ID == "" {
		t.Fatal("expected a non-empty raid ID")
	}

	got, err := store.Get(raid.ID)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if got.ID != raid.ID {
		t.Fatalf("expected to fetch the same raid back, got a different one")
	}
}

func TestCreateRaidRejectsNonPositiveMaxHP(t *testing.T) {
	store := NewStore()
	raid := store.CreateRaid("Groudon", 60, 0)
	if raid.MaxHP != 1 || raid.HP != 1 {
		t.Fatalf("expected non-positive max_hp to be clamped to 1, got %d", raid.MaxHP)
	}
}

func TestGetUnknownRaid(t *testing.T) {
	store := NewStore()
	if _, err := store.Get("does-not-exist"); err != ErrRaidNotFound {
		t.Fatalf("expected ErrRaidNotFound, got %v", err)
	}
}

func TestJoinAddsParticipantOnce(t *testing.T) {
	store := NewStore()
	raid := store.CreateRaid("Kyogre", 60, 300)

	if _, err := store.Join(raid.ID, "ash"); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if _, err := store.Join(raid.ID, "ash"); err != nil {
		t.Fatalf("unexpected error joining twice: %v", err)
	}

	got, _ := store.Get(raid.ID)
	if len(got.Participants) != 1 {
		t.Fatalf("expected exactly 1 participant after joining twice, got %d", len(got.Participants))
	}
}

func TestJoinRejectsEmptyUsername(t *testing.T) {
	store := NewStore()
	raid := store.CreateRaid("Kyogre", 60, 300)
	if _, err := store.Join(raid.ID, ""); err != ErrParticipantEmpty {
		t.Fatalf("expected ErrParticipantEmpty, got %v", err)
	}
}

func TestAttackClampsAbsurdDamageClaim(t *testing.T) {
	store := NewStore()
	raid := store.CreateRaid("Mewtwo", 70, 1000)

	// A claimed 999999 damage from a level 5, 40-base-power move must be
	// clamped down to a physically-plausible ceiling, not applied as-is.
	_, accepted, err := store.Attack(raid.ID, "cheater", 999999, 5, 40, 20, 20)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if accepted >= 999999 {
		t.Fatalf("expected damage to be clamped, got %d accepted", accepted)
	}

	got, _ := store.Get(raid.ID)
	if got.HP != 1000-accepted {
		t.Fatalf("expected raid HP to drop by exactly the accepted damage, got HP=%d accepted=%d", got.HP, accepted)
	}
}

func TestAttackReasonableDamagePassesThrough(t *testing.T) {
	store := NewStore()
	raid := store.CreateRaid("Mewtwo", 70, 1000)

	_, accepted, err := store.Attack(raid.ID, "trainer", 15, 20, 40, 50, 40)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if accepted != 15 {
		t.Fatalf("expected a reasonable damage claim to pass through unclamped, got %d", accepted)
	}
}

func TestAttackOnDefeatedRaidFails(t *testing.T) {
	store := NewStore()
	raid := store.CreateRaid("Deoxys", 50, 10)

	if _, _, err := store.Attack(raid.ID, "trainer", 10, 50, 40, 40, 10); err != nil {
		t.Fatalf("unexpected error on defeating hit: %v", err)
	}
	got, _ := store.Get(raid.ID)
	if !got.IsDefeated() {
		t.Fatalf("expected raid to be defeated, HP=%d", got.HP)
	}

	if _, _, err := store.Attack(raid.ID, "trainer", 10, 50, 40, 40, 10); err != ErrRaidAlreadyOver {
		t.Fatalf("expected ErrRaidAlreadyOver, got %v", err)
	}
}

func TestListActiveExcludesDefeatedRaids(t *testing.T) {
	store := NewStore()
	alive := store.CreateRaid("Alive", 50, 100)
	dead := store.CreateRaid("Dead", 50, 5)
	store.Attack(dead.ID, "trainer", 999, 50, 40, 40, 10)

	active := store.ListActive()
	if len(active) != 1 || active[0].ID != alive.ID {
		t.Fatalf("expected only the alive raid to be listed, got %d raids", len(active))
	}
}

func TestConcurrentAttacksDoNotRace(t *testing.T) {
	store := NewStore()
	raid := store.CreateRaid("Groudon", 60, 100000)

	const goroutines = 50
	var wg sync.WaitGroup
	wg.Add(goroutines)
	for i := 0; i < goroutines; i++ {
		go func(n int) {
			defer wg.Done()
			store.Attack(raid.ID, "trainer", 10, 50, 40, 40, 10)
		}(i)
	}
	wg.Wait()

	got, _ := store.Get(raid.ID)
	totalDamage := 0
	for _, p := range got.Participants {
		totalDamage += p.DamageDealt
	}
	if got.HP != 100000-totalDamage {
		t.Fatalf("HP (%d) doesn't match total tracked damage (%d) - lost updates under concurrency", got.HP, totalDamage)
	}
}
