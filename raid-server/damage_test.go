package main

import "testing"

func TestMaxPossibleDamageClampsInvalidInputsInsteadOfZero(t *testing.T) {
	// Non-positive/out-of-range inputs get clamped to sane bounds (not
	// treated as "zero damage") - a client can't zero out or invert the
	// ceiling by sending garbage.
	baseline := maxPossibleDamage(10, 40, 50, 50)
	cases := [][4]int{
		{0, 40, 50, 50},
		{10, 0, 50, 50},
		{10, 40, 0, 50},
		{10, 40, 50, 0},
	}
	for _, c := range cases {
		got := maxPossibleDamage(c[0], c[1], c[2], c[3])
		if got <= 0 {
			t.Errorf("maxPossibleDamage(%v) = %d, want a clamped positive ceiling", c, got)
		}
		_ = baseline
	}
}

func TestMaxPossibleDamageClampsAbsurdInputsUpward(t *testing.T) {
	// A client claiming an absurd level/stat to inflate its own damage
	// ceiling must not get a bigger ceiling than the in-game max would give.
	realistic := maxPossibleDamage(100, 250, 999, 1)
	gamed := maxPossibleDamage(999999999, 999999999, 999999999, 1)
	if gamed != realistic {
		t.Fatalf("expected absurd inputs to clamp to the same ceiling as max realistic inputs (%d), got %d", realistic, gamed)
	}
}

func TestMaxPossibleDamageIncreasesWithLevel(t *testing.T) {
	low := maxPossibleDamage(5, 40, 50, 50)
	high := maxPossibleDamage(50, 40, 50, 50)
	if high <= low {
		t.Fatalf("expected higher level to raise the damage ceiling: low=%d high=%d", low, high)
	}
}

func TestMaxPossibleDamageNeverExceedsHardCeiling(t *testing.T) {
	got := maxPossibleDamage(100, 250, 999, 1)
	if got > 1_000_000 {
		t.Fatalf("expected the hard ceiling to cap even the most extreme legal inputs, got %d", got)
	}
}

func TestClampDamagePassesThroughReasonableClaims(t *testing.T) {
	ceiling := maxPossibleDamage(20, 40, 50, 50)
	reasonable := ceiling / 2
	if got := clampDamage(reasonable, 20, 40, 50, 50); got != reasonable {
		t.Fatalf("expected reasonable damage to pass through unclamped, got %d want %d", got, reasonable)
	}
}

func TestClampDamageCapsAtCeiling(t *testing.T) {
	ceiling := maxPossibleDamage(20, 40, 50, 50)
	if got := clampDamage(ceiling*100, 20, 40, 50, 50); got != ceiling {
		t.Fatalf("expected damage to be clamped to the ceiling (%d), got %d", ceiling, got)
	}
}

func TestClampDamageRejectsNegative(t *testing.T) {
	if got := clampDamage(-50, 20, 40, 50, 50); got != 0 {
		t.Fatalf("expected negative damage to clamp to 0, got %d", got)
	}
}
