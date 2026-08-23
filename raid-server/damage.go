package main

// clampDamage bounds a client-submitted damage number to a theoretical
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
func maxPossibleDamage(level, basePower, atkStat, defStat int) int {
	if level <= 0 || basePower <= 0 || atkStat <= 0 || defStat <= 0 {
		return 0
	}

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
	if dmg < 0 {
		return 0
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
