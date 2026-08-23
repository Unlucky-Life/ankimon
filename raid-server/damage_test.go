package main

import "testing"

func TestMaxPossibleDamageZeroOnInvalidInput(t *testing.T) {
	cases := [][4]int{
		{0, 40, 50, 50},
		{10, 0, 50, 50},
		{10, 40, 0, 50},
		{10, 40, 50, 0},
	}
	for _, c := range cases {
		if got := maxPossibleDamage(c[0], c[1], c[2], c[3]); got != 0 {
			t.Errorf("maxPossibleDamage(%v) = %d, want 0", c, got)
		}
	}
}

func TestMaxPossibleDamageIncreasesWithLevel(t *testing.T) {
	low := maxPossibleDamage(5, 40, 50, 50)
	high := maxPossibleDamage(50, 40, 50, 50)
	if high <= low {
		t.Fatalf("expected higher level to raise the damage ceiling: low=%d high=%d", low, high)
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
