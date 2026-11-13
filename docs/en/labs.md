# 4.2 Four offline experiments

> Condensed English reading notes. The Chinese edition contains the full worked lesson.

## Four small experiments without external services

Run the modules from the repository root with Python 3.11 or newer. They use the standard library and fictional data.

`python3 -m labs.gradient` checks one gradient step and an overshoot counterexample. `python3 -m labs.attention` shows stable softmax, weighted values and a causal mask. `python3 -m labs.retrieval` separates authorized candidates from evidence completeness. `python3 -m labs.recovery` simulates a crash after an independent external database commit and resumes with one idempotency key.

Run `python3 -m unittest discover -s tests -v` to check these local properties. The recovery example relies on its simulated external service supporting idempotency. These experiments do not train a large model, benchmark semantic retrieval or implement a production agent.

## Check your understanding

What should remain after recovery?

<details><summary>Suggested answer</summary>

One external draft and a local completed task referring to the same draft receipt, even after connections are closed and reopened.

</details>
