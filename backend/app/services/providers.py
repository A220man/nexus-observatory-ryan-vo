"""Registry of cloud-disk share providers.

Each provider declares the domains and URL patterns it owns and the deterministic
rule that derives a *direct-link strategy* from a parsed share. The strategy is a
documented, honest description of what a full client would need; the engine does
not fabricate working download URLs it cannot verify offline.

The registry is the deterministic baseline: it is the "no-ML" core that always
works so the product never depends on a model key.
"""
from __future__ import annotations

import dataclasses
import re
from typing import Optional


@dataclasses.dataclass(frozen=True)
class Provider:
    """A supported cloud-disk sharing provider."""
    key: str              # machine id, e.g. "baidu"
    name: str            # display name
    domains: tuple[str, ...]  # host suffixes this provider owns
    patterns: tuple[str, ...]  # regex patterns; capture group 1 is the resource id
    password_param: Optional[str]  # query/form param carrying a share password, or None
    strategy: str        # human-readable direct-link strategy

    def matches(self, host: str) -> bool:
        h = host.lower()
        return any(h == d or h.endswith("." + d) for d in self.domains)

    def parse(self, url: str) -> Optional[tuple[str, Optional[str]]]:
        """Return (resource_id, password) if URL matches, else None.

        The resource id is capture group 1 of the first matching pattern; an
        optional password group (group 2) is captured where the provider embeds
        one in the share URL.
        """
        for pat in self.patterns:
            m = re.search(pat, url)
            if m:
                resource_id = m.group(1)
                password = m.group(2) if m.lastindex and m.lastindex >= 2 else None
                return resource_id, password
        return None


# Eight major cloud-disk providers (see product brief "八大网盘").
PROVIDERS: tuple[Provider, ...] = (
    Provider(
        key="baidu",
        name="Baidu Cloud",
        domains=("pan.baidu.com", "yun.baidu.com"),
        patterns=(
            r"pan\.baidu\.com/s/([A-Za-z0-9_-]+)(?:\?pwd=([A-Za-z0-9]+))?",
            r"yun\.baidu\.com/s/([A-Za-z0-9_-]+)(?:\?pwd=([A-Za-z0-9]+))?",
        ),
        password_param="pwd",
        strategy="baidu:s/2.0/ share/uk/file with stoken (requires /app/config and a "
                   "login token; not reproducible offline)",
    ),
    Provider(
        key="aliyun",
        name="Aliyun Disk",
        domains=("aliyuncloud.com",),
        patterns=(
            r"aliyuncloud\.com/s/([A-Za-z0-9_-]+)(?:\?pwd=([A-Za-z0-9]+))?",
            r"aliyuncloud\.com/share/([A-Za-z0-9_-]+)(?:\?pwd=([A-Za-z0-9]+))?",
        ),
        password_param="pwd",
        strategy="aliyun: /s/:id resolves to a share; direct file links come from a "
                 "signed /api/v1/share/download/url using a refresh token",
    ),
    Provider(
        key="cmcc",
        name="China Mobile Cloud",
        domains=("yun.139.com", "139ym.com"),
        patterns=(
            r"yun\.139\.com/.+/([A-Za-z0-9]{10,})",
        ),
        password_param="password",
        strategy="cmcc: 139 yun share requires a /api/open/share/check code + phone "
                 "captcha before a signed downloadUrl is returned",
    ),
    Provider(
        key="tianyi",
        name="Tianyi Cloud",
        domains=("cloud.189.com",),
        patterns=(
            r"cloud\.189\.com/web/share/([A-Za-z0-9_-]+)(?:\?accessCode=([A-Za-z0-9]+))?",
            r"cloud\.189\.com/share/([A-Za-z0-9_-]+)(?:\?accessCode=([A-Za-z0-9]+))?",
        ),
        password_param="accessCode",
        strategy="tianyi: /web/share/:id calls open/api/cubic/getThumbnailsInfo "
                 "then a signed download URL via open/api/cubic/download",
    ),
    Provider(
        key="xunlei",
        name="Xunlei Cloud",
        domains=("pan.xunlei.com", "yunpan.xunlei.com"),
        patterns=(
            r"pan\.xunlei\.com/s/([A-Za-z0-9_-]+)(?:\?pwd=([A-Za-z0-9]+))?",
        ),
        password_param="pwd",
        strategy="xunlei: /s/:id returns a Thunder (xlp) short id; direct link needs "
                 "the /api/vip/user/login + /api/download/transfer chain with a cookie",
    ),
    Provider(
        key="qiniu",
        name="Qiniu Cloud Disk",
        domains=("qiniu.com",),
        patterns=(
            r"qiniu\.com/s/([A-Za-z0-9_-]+)",
        ),
        password_param=None,
        strategy="qiniu: share resolves on /api/v1/share/:id; download via a signed "
                 "qiniu CDN URL returned by the share API",
    ),
    Provider(
        key="uc",
        name="UC Cloud",
        domains=("pan.uc.com", "www.uc.cn"),
        patterns=(
            r"pan\.uc\.com/s/([A-Za-z0-9_-]+)(?:\?code=([A-Za-z0-9]+))?",
            r"uc\.cn/s/([A-Za-z0-9_-]+)(?:\?code=([A-Za-z0-9]+))?",
        ),
        password_param="code",
        strategy="uc: /s/:id is a share code; UC returns a signed download_url after "
                 "a /api/share/check password/captcha step",
    ),
    Provider(
        key="wy123",
        name="123 Cloud",
        domains=("www.123pan.com",),
        patterns=(
            r"123pan\.com/s/([A-Za-z0-9_-]+)(?:\?pwd=([A-Za-z0-9]+))?",
        ),
        password_param="pwd",
        strategy="wy123: /s/:id maps to a cloud file listing API; direct links are "
                 "signed URLs expiring in 30 minutes",
    ),
)

# Fast lookup by key.
BY_KEY: dict[str, Provider] = {p.key: p for p in PROVIDERS}


def provider_for_url(url: str) -> Optional[Provider]:
    """Identify the provider for a share URL by host match first, then pattern."""
    host = _host(url)
    if host:
        for p in PROVIDERS:
            if p.matches(host) and p.parse(url) is not None:
                return p
    for p in PROVIDERS:
        if p.parse(url) is not None:
            return p
    return None


def _host(url: str) -> str:
    # Avoid importing urllib for perf; a simple slice is enough.
    m = re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://([^/?#]+)", url)
    return m.group(1) if m else ""


def list_providers() -> list[dict[str, object]]:
    return [
        {
            "key": p.key,
            "name": p.name,
            "domains": list(p.domains),
            "password_param": p.password_param,
            "strategy": p.strategy,
        }
        for p in PROVIDERS
    ]