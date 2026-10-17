"""Labeled dataset of cloud-disk sharing URLs for the 8 providers.

Every example is synthetic but follows the URL shapes each provider advertises
on its web sharing pages.  Labels use the provider keys registered in
``providers.py``.  This dataset is the training + test corpus for the from-scratch
TF-IDF / logistic-regression classifier in ``classifier.py``.
"""
from __future__ import annotations

from typing import NamedTuple

#: Canonical ordered set of provider keys (mirrors PROVIDERS ordering).
PROVIDER_KEYS: tuple[str, ...] = (
    "baidu",
    "aliyun",
    "cmcc",
    "tianyi",
    "xunlei",
    "qiniu",
    "uc",
    "wy123",
)


class LabeledURL(NamedTuple):
    """A single labeled training / test sample."""

    url: str
    label: str  # provider key


#: Eight providers — six to eight synthetic-but-pattern-faithful URLs each.
DATASET: list[LabeledURL] = [
    # ── Baidu Cloud ──────────────────────────────────────────────
    # Shape: pan|yun.baidu.com/s/<id>   or   ...?pwd=<chars>
    LabeledURL("https://pan.baidu.com/s/1aF2xYz9KpLmN3oQrS", "baidu"),
    LabeledURL("https://pan.baidu.com/s/1BcDdEeFfGgHhIiJjKk?pwd=1234", "baidu"),
    LabeledURL("https://yun.baidu.com/s/1XxYyZzAaBbCcDdEeFf", "baidu"),
    LabeledURL("https://pan.baidu.com/s/1mNpOqRsTuVwXyZ0aBcD?pwd=abcd", "baidu"),
    LabeledURL("https://pan.baidu.com/s/1zYxWvUtSrQpOnMlKjIh", "baidu"),
    LabeledURL("https://yun.baidu.com/s/1aAbBcCdDeEfFgGhHiIj?pwd=9999", "baidu"),
    LabeledURL("https://pan.baidu.com/s/1AaBbCcDdEeFfGgHhIiJ", "baidu"),
    LabeledURL("https://yun.baidu.com/s/1ZsXwCvBnMpOiUtyHgFe?pwd=qwer", "baidu"),
    # ── Aliyun Disk ──────────────────────────────────────────────
    # Shape: aliyuncloud.com/s/<id>   or   /share/<id>   or   ?pwd=<chars>
    LabeledURL("https://aliyuncloud.com/s/AbCdEfGhIjKlMnOp", "aliyun"),
    LabeledURL("https://aliyuncloud.com/s/XyZw1234AbCd5678?pwd=1234", "aliyun"),
    LabeledURL("https://aliyuncloud.com/share/1a2b3c4d5e6f7g8h", "aliyun"),
    LabeledURL("https://aliyuncloud.com/s/AaBbCcDdEeFfGgHh?pwd=abcd", "aliyun"),
    LabeledURL("https://aliyuncloud.com/share/ZzYyXxWwVvUuTsSr", "aliyun"),
    LabeledURL("https://aliyuncloud.com/s/9x8w7v6u5t4s3r2q?pwd=5678", "aliyun"),
    LabeledURL("https://aliyuncloud.com/share/KlMnOpQrStUvWxYz", "aliyun"),
    # ── China Mobile Cloud ───────────────────────────────────────
    # Shape: yun.139.com/share/<id>   or   139ym.com/share/<id>
    LabeledURL("https://yun.139.com/share/a1b2c3d4e5f6g7h8i9j0", "cmcc"),
    LabeledURL("https://yun.139.com/share/xY6w5v4u3t2s1r0q9p8o", "cmcc"),
    LabeledURL("https://139ym.com/share/abcdef1234567890abcd", "cmcc"),
    LabeledURL("https://yun.139.com/share/9f8e7d6c5b4a3210zyxw", "cmcc"),
    LabeledURL("https://yun.139.com/share/mNoPqRsTuVwXyZ0aBcDeF", "cmcc"),
    LabeledURL("https://139ym.com/share/12345abcdef67890ghijkl", "cmcc"),
    # ── Tianyi Cloud ─────────────────────────────────────────────
    # Shape: cloud.189.com/web/share/<id>   or   /share/<id>   or   ?accessCode=
    LabeledURL("https://cloud.189.com/web/share/abc123def456ghi", "tianyi"),
    LabeledURL("https://cloud.189.com/share/xyz789abc456def", "tianyi"),
    LabeledURL("https://cloud.189.com/web/share/AaBbCcDdEeFfGgHh?accessCode=1234", "tianyi"),
    LabeledURL("https://cloud.189.com/web/share/zzyyxxwwvvuuts", "tianyi"),
    LabeledURL("https://cloud.189.com/web/share/ABCDEF1234567890?accessCode=abcd", "tianyi"),
    LabeledURL("https://cloud.189.com/share/0987654321fedcba", "tianyi"),
    # ── Xunlei Cloud ─────────────────────────────────────────────
    # Shape: pan.xunlei.com/s/<id>   or   yunpan.xunlei.com/s/<id>   or   ?pwd=
    LabeledURL("https://pan.xunlei.com/s/a1b2c3d4e5f6g7h8", "xunlei"),
    LabeledURL("https://pan.xunlei.com/s/abcd1234efgh5678?pwd=1234", "xunlei"),
    LabeledURL("https://yunpan.xunlei.com/s/xyzxyzxyzxyzxyzx", "xunlei"),
    LabeledURL("https://pan.xunlei.com/s/1234567890abcdefgh", "xunlei"),
    LabeledURL("https://pan.xunlei.com/s/QqWwEeRrTtYyUuIi?pwd=abcd", "xunlei"),
    LabeledURL("https://yunpan.xunlei.com/s/mNPQRSTUVWXYZ12345", "xunlei"),
    # ── Qiniu Cloud Disk ─────────────────────────────────────────
    # Shape: qiniu.com/s/<id>
    LabeledURL("https://qiniu.com/s/abc123def456ghi789", "qiniu"),
    LabeledURL("https://qiniu.com/s/xyz789abc456def123", "qiniu"),
    LabeledURL("https://qiniu.com/s/abcdef1234567890ab", "qiniu"),
    LabeledURL("https://qiniu.com/s/ZzYyXxWwVvUuTsSrQq", "qiniu"),
    LabeledURL("https://qiniu.com/s/1234567890abcdefg", "qiniu"),
    LabeledURL("https://qiniu.com/s/AaBbCcDdEeFfGgHhIi", "qiniu"),
    # ── UC Cloud ─────────────────────────────────────────────────
    # Shape: pan.uc.com/s/<id>?code=<chars>   or   uc.cn/s/<id>
    LabeledURL("https://pan.uc.com/s/abc123def456ghi789?code=1234", "uc"),
    LabeledURL("https://pan.uc.com/s/xyz789abc456def123?code=abcd", "uc"),
    LabeledURL("https://uc.cn/s/abcdef1234567890ab?code=9999", "uc"),
    LabeledURL("https://pan.uc.com/s/1234567890abcdefgh?code=0000", "uc"),
    LabeledURL("https://pan.uc.com/s/IjKlMnOpQrStUvWxYz?code=5678", "uc"),
    LabeledURL("https://uc.cn/s/AaBbCcDdEeFfGgHhIi?code=qwer", "uc"),
    # ── 123 Cloud ────────────────────────────────────────────────
    # Shape: www.123pan.com/s/<id>   or   ?pwd=<chars>
    LabeledURL("https://www.123pan.com/s/abc123def456ghi789", "wy123"),
    LabeledURL("https://www.123pan.com/s/xyz789abc456def123?pwd=1234", "wy123"),
    LabeledURL("https://www.123pan.com/s/abcdef1234567890ab", "wy123"),
    LabeledURL("https://www.123pan.com/s/ZzYyXxWwVvUuTsSrQq?pwd=abcd", "wy123"),
    LabeledURL("https://www.123pan.com/s/9876543210zyxwvuts", "wy123"),
    LabeledURL("https://www.123pan.com/s/MmNnOoPpQqRrSsTt?pwd=9999", "wy123"),
]

#: Number of training / test samples when splitting 80/20 per class.
TRAIN_FRACTION = 0.8