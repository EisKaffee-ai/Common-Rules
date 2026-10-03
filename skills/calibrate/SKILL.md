---
name: calibrate
description: Recalibrate Common Rules when repositories, roles, requirement or tracker locations, issue linkage, or delivery constraints change.
---

# Common Rules recalibration

Say which changed context selected this skill. Read `.common-rules.json`, the
workspace manifest when present, and current repository evidence. Preview the
smallest manifest change, preserve unknown keys, and explain whether the change
affects only local paths or committed project truth. Apply only with explicit
approval, then run doctor and tracecheck.
