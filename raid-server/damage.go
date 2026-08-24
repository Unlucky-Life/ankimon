package main

import "math"

// Sane bounds for the inputs used to compute a damage ceiling. Pokemon stats
// and levels are bounded in the real game; a client claiming, say, level
// 999999999 to blow the ceiling wide open (or overflow the float64->int
// conversion below) gets clamped to these before anything is computed.
const (
	minLevel = 1
	maxLevel = 100

	minStat = 1
	maxStat = 999 // generous ceiling above any real in-game stat (even fully IV/EV maxed + boosted)

	minBasePower = 1
	maxBasePower = 250 // highest base power moves in the addon's data top out well under this
)

func clampInt(v, lo, hi int) int {
	if v < lo {
		return lo
	}
	if v > hi {
		return hi
	}
	return v
}

// maxPossibleDamage bounds a client-submitted damage number to a theoretical
// ceiling derived from the same formula the addon uses client-side
// (functions/battle_functions.py: calc_atk_dmg), so one participant can't
// claim arbitrary damage against the shared boss.
//
// This is deliberately an approximation, not a byte-for-byte reimplementation
// of the Python formula: it doesn't have access to the addon's type
// effectiveness chart, so it assumes the most generous case for every
// variable that isn't sent by the client (max crit, max STAB, max dual-type
// effectiveness, max random-luck roll). That means a legitimate hit is
// always allowed through; only physically-impossible claims get clamped.
//
// All inputs are clamped to real-game-plausible ranges first - both to stop
// someone gaming the ceiling upward by claiming an absurd level/stat, and to
// keep the float64 math (and the final conversion back to int) well inside
// safe range.
func maxPossibleDamage(level, basePower, atkStat, defStat int) int {
	level = clampInt(level, minLevel, maxLevel)
	basePower = clampInt(basePower, minBasePower, maxBasePower)
	atkStat = clampInt(atkStat, minStat, maxStat)
	defStat = clampInt(defStat, minStat, maxStat)

	const (
		maxCriticalMultiplier = 4.0 // observed ceiling of the addon's "critical" (round-performance x crit) term
		maxStab               = 1.5
		maxEffectiveness      = 4.0 // double-super-effective across a dual type
		maxRandomFactor       = 1.0 // random.randint(217,255)/255 tops out at 1.0
	)

	l := float64(level)
	p := float64(basePower)
	atk := float64(atkStat)
	def := float64(defStat)

	dmg := ((((2*l*maxCriticalMultiplier)+2)/5)*p*atk/def + 2) / 50 * maxStab * maxEffectiveness * maxRandomFactor

	// With the clamps above this can no longer realistically approach
	// MaxInt, but guard the float->int conversion anyway: converting a
	// float64 that's NaN, +/-Inf, or out of the int range is undefined
	// behaviour in Go, not a clean saturation.
	if math.IsNaN(dmg) || dmg < 0 {
		return 0
	}
	const hardCeiling = 1_000_000
	if dmg > hardCeiling {
		return hardCeiling
	}
	return int(dmg)
}

// clampDamage returns claimedDamage clamped to [0, maxPossibleDamage(...)].
func clampDamage(claimedDamage, level, basePower, atkStat, defStat int) int {
	if claimedDamage < 0 {
		return 0
	}
	ceiling := maxPossibleDamage(level, basePower, atkStat, defStat)
	if claimedDamage > ceiling {
		return ceiling
	}
	return claimedDamage
}
