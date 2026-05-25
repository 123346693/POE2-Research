from __future__ import annotations

from dataclasses import dataclass


API_ROOT = "https://api.pathofexile.com"
OAUTH_ROOT = "https://www.pathofexile.com/oauth"


@dataclass(frozen=True)
class OfficialApiCapability:
    name: str
    scope: str
    poe2_status: str
    notes: str


CAPABILITIES = (
    OfficialApiCapability(
        name="account characters",
        scope="account:characters",
        poe2_status="available with user OAuth",
        notes="Needed for importing a player's own character inventory and passive data.",
    ),
    OfficialApiCapability(
        name="leagues",
        scope="service:leagues",
        poe2_status="available with realm=poe2",
        notes="Needed to discover current POE2 leagues before pricing and recommendation.",
    ),
    OfficialApiCapability(
        name="currency exchange history",
        scope="service:cxapi",
        poe2_status="available with realm=poe2",
        notes="Historical hourly currency markets; not current-hour live pricing.",
    ),
)


def describe_capabilities() -> tuple[OfficialApiCapability, ...]:
    return CAPABILITIES
