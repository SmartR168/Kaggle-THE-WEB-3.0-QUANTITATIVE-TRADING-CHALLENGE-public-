"""Chronological validation with an explicit purge between train and test."""

from __future__ import annotations

from collections.abc import Iterator

import numpy as np


def walk_forward_splits(
    n_samples: int,
    *,
    min_train_size: int,
    test_size: int,
    purge_size: int,
) -> Iterator[tuple[np.ndarray, np.ndarray]]:
    """Yield expanding-window train/test indices with a purge gap."""

    if min_train_size <= 0 or test_size <= 0 or purge_size < 0:
        raise ValueError("split sizes must be positive and purge_size non-negative")
    if min_train_size + purge_size + test_size > n_samples:
        raise ValueError("not enough observations for one split")

    train_end = min_train_size
    while train_end + purge_size + test_size <= n_samples:
        test_start = train_end + purge_size
        yield np.arange(0, train_end), np.arange(test_start, test_start + test_size)
        train_end += test_size
