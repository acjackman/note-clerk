---
created: {{ now_utc|strftime("%Y-%m-%dT%H:%M:%S") }}Z
type: note/plan/day
alias: ["{{ date|strftime("%Y-%m-%d") }}"]
---
# {{ date|strftime("%A %Y-%m-%d") }}
**Week:** {{ date|week_link }}
**Yesterday:** {{ day(-1) }}
**Tomorrow:** {{ day(1) }}

## Plan

## Log
