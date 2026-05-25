from __future__ import annotations

from .models import Build, ScoreResult, UserProfile


BUDGET_RANK = {
    "starter": 1,
    "low": 1,
    "medium": 2,
    "mid": 2,
    "high": 3,
    "expensive": 3,
    "mirror": 4,
}

NERF_RISK_PENALTY = {
    "low": 0.0,
    "medium": -4.0,
    "high": -10.0,
}


def score_build(build: Build, profile: UserProfile) -> ScoreResult:
    weights = _weights_for(profile)
    components: dict[str, float] = {}
    total = 0.0

    for metric, weight in weights.items():
        value = _metric(build, metric)
        components[metric] = value * weight
        total += components[metric]

    strengths: list[str] = []
    concerns: list[str] = []

    fit_score, fit_strengths, fit_concerns = _fit_adjustment(build, profile)
    total += fit_score
    components["user_fit"] = fit_score
    strengths.extend(fit_strengths)
    concerns.extend(fit_concerns)

    nerf_penalty = NERF_RISK_PENALTY.get(build.nerf_risk, -4.0)
    total += nerf_penalty
    components["nerf_risk"] = nerf_penalty
    if build.nerf_risk == "high":
        concerns.append("High nerf risk for the current snapshot.")
    elif build.nerf_risk == "low":
        strengths.append("Low nerf-risk profile.")

    if _metric(build, "data_confidence") < 50:
        concerns.append("Low data confidence: treat as a candidate, not a verdict.")

    return ScoreResult(
        build=build,
        total=round(total, 2),
        strengths=tuple(strengths),
        concerns=tuple(concerns),
        component_scores={key: round(value, 2) for key, value in components.items()},
    )


def _weights_for(profile: UserProfile) -> dict[str, float]:
    weights = {
        "damage": 0.20,
        "clear_speed": 0.18,
        "survivability": 0.20,
        "cost_efficiency": 0.14,
        "patch_stability": 0.10,
        "ssf_viability": 0.06,
        "ease_of_play": 0.07,
        "data_confidence": 0.05,
    }

    playstyles = set(profile.playstyles)
    if "bossing" in playstyles:
        weights["damage"] += 0.10
        weights["clear_speed"] -= 0.05
        weights["survivability"] += 0.03
        weights["ease_of_play"] -= 0.03
    if "mapping" in playstyles:
        weights["clear_speed"] += 0.10
        weights["damage"] -= 0.03
        weights["survivability"] -= 0.02
    if "starter" in playstyles or profile.budget in {"starter", "low"}:
        weights["cost_efficiency"] += 0.08
        weights["ssf_viability"] += 0.04
        weights["data_confidence"] += 0.03
        weights["damage"] -= 0.05
    if profile.hardcore or "hardcore" in playstyles:
        weights["survivability"] += 0.15
        weights["patch_stability"] += 0.04
        weights["clear_speed"] -= 0.07
        weights["damage"] -= 0.05
    if profile.trade_mode == "ssf":
        weights["ssf_viability"] += 0.12
        weights["cost_efficiency"] += 0.04
        weights["damage"] -= 0.04

    total = sum(weights.values())
    return {key: value / total for key, value in weights.items()}


def _fit_adjustment(build: Build, profile: UserProfile) -> tuple[float, list[str], list[str]]:
    score = 0.0
    strengths: list[str] = []
    concerns: list[str] = []

    if profile.player_class:
        if build.player_class.lower() == profile.player_class.lower():
            score += 8.0
            strengths.append(f"Matches requested class: {build.player_class}.")
        else:
            score -= 12.0
            concerns.append(f"Different class: {build.player_class}.")

    if profile.ascendancy:
        if build.ascendancy.lower() == profile.ascendancy.lower():
            score += 8.0
            strengths.append(f"Matches requested ascendancy: {build.ascendancy}.")
        else:
            score -= 8.0
            concerns.append(f"Different ascendancy: {build.ascendancy}.")

    build_tags = set(build.tags)
    for playstyle in profile.playstyles:
        if playstyle in build_tags:
            score += 5.0
            strengths.append(f"Tagged for {playstyle}.")
        else:
            score -= 2.0

    requested_budget = BUDGET_RANK.get(profile.budget, 2)
    build_budget = BUDGET_RANK.get(build.budget, 2)
    if profile.budget_divines is not None and build.estimated_cost_divines is not None:
        if build.estimated_cost_divines <= profile.budget_divines:
            score += 7.0
            strengths.append(
                f"Fits currency budget: {build.estimated_cost_divines:g}D <= {profile.budget_divines:g}D."
            )
        else:
            over = build.estimated_cost_divines - profile.budget_divines
            score -= min(25.0, 5.0 + over * 1.5)
            concerns.append(
                f"Over currency budget: estimated {build.estimated_cost_divines:g}D, requested {profile.budget_divines:g}D."
            )
    elif build_budget <= requested_budget:
        score += 5.0
        strengths.append(f"Fits budget: {build.budget}.")
    else:
        penalty = 7.0 * (build_budget - requested_budget)
        score -= penalty
        concerns.append(f"Over budget: build is {build.budget}, requested {profile.budget}.")

    if profile.trade_mode == "ssf":
        if build.trade_mode in {"ssf", "either"}:
            score += 4.0
            strengths.append("Usable in SSF.")
        else:
            score -= 12.0
            concerns.append("Trade-only profile conflicts with SSF request.")
    elif profile.trade_mode == "trade" and build.trade_mode == "ssf":
        score -= 1.0

    if profile.hardcore:
        survivability = _metric(build, "survivability")
        if survivability >= 80:
            score += 8.0
            strengths.append("HC-friendly survivability.")
        else:
            score -= 12.0
            concerns.append("Survivability may be too low for HC.")

    if profile.min_survivability is not None:
        survivability = _metric(build, "survivability")
        if survivability < profile.min_survivability:
            gap = profile.min_survivability - survivability
            score -= min(20.0, gap * 0.5)
            concerns.append(
                f"Below minimum survivability: {survivability:.0f} < {profile.min_survivability:.0f}."
            )

    if profile.avoid_uniques and build.required_uniques:
        score -= min(18.0, 4.0 * len(build.required_uniques))
        concerns.append("Requires unique/core special items.")

    if profile.controller_friendly:
        if "controller" in build_tags:
            score += 4.0
            strengths.append("Controller-friendly tag present.")
        else:
            score -= 3.0

    return score, strengths, concerns


def _metric(build: Build, key: str) -> float:
    value = build.metrics.get(key, 50.0)
    return max(0.0, min(100.0, float(value)))
