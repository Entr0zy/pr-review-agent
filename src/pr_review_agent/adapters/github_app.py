"""GitHub App adapter — TARGET: the product/portfolio lane (GitHub Marketplace).

Plan:
  1. A GitHub App subscribes to `pull_request` webhook events.
  2. On open/synchronize, fetch the PR diff via the REST API.
  3. `PRReviewer.review_diff` produces findings, posted as a Check Run +
     inline review comments.

This is the path to a sellable Marketplace listing once the core is proven in
the hackathons. Stub for now.
"""
from __future__ import annotations


def on_pull_request(payload: dict) -> None:
    raise NotImplementedError(
        "Verify the webhook signature, fetch the diff, then reuse PRReviewer."
    )
