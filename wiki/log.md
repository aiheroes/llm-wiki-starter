---
type: log
status: reviewed
---

# Log

Append only. Newest at the bottom. One entry per ingest, lint or decision.

Format:

```
## YYYY-MM-DD · ingest | query | lint | decision · short title
- Source: [[src-slug]] (raw/file)
- Created: [[page]], [[page]]
- Changed: [[page]]
- Contradictions: what disagrees with what, both citations; see review queue
```
