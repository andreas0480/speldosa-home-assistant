"""Which music account plays a tag on a box.

A tag's URI names the Music Assistant provider instance it was linked from, for example
spotify--Vf8xo62o://album/<id>. With two accounts of one service in Music Assistant (two Spotify family members),
a box can be set to play through its own account: the instance part is swapped, the item id stays, since every
account of a service sees the same catalogue.
"""

from __future__ import annotations

import re

_URI = re.compile(r"^(?P<instance>[A-Za-z0-9_]+(?:--[A-Za-z0-9]+)?)://")


def provider_domain(instance_id: str) -> str:
    """spotify--Vf8xo62o -> spotify; spotify -> spotify."""
    return instance_id.split("--", 1)[0]


def with_account(uri: str | None, account: str | None) -> str | None:
    """uri played through the provider instance `account`, when the uri belongs to the same service.

    Anything else (no account set, another service, library:// items, plain URLs) is returned unchanged.
    """
    if not uri or not account:
        return uri
    match = _URI.match(uri)
    if match is None or match.group("instance") == account:
        return uri
    if provider_domain(match.group("instance")) != provider_domain(account):
        return uri
    return account + uri[match.end("instance"):]
