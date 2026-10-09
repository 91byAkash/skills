# Workflow: <name>

## Purpose
<one or two lines: what this workflow produces and for whom>

## Trigger
- Type: event | schedule
- Source: <e.g. new message in support inbox / every Monday 09:00 local>
- De-duplication: <how a repeated trigger is detected and skipped>

## Inputs
| Input | Where it comes from | Format | Required |
|---|---|---|---|

## Steps
1. <step> (automated | AI | human)
2. ...

## Checkpoints
| Where | Who | Brief contents | Decision options | Timeout behaviour |
|---|---|---|---|---|

## Output
- Artifact: <file, message, ticket, record>
- Destination: <where it lands>
- Format: <template or schema>

## Failure handling
- If <dependency> is unavailable: <retry N times / skip / alert whom>
- If input is malformed: <...>

## Done / success criteria
- <observable check that a run succeeded>

## Open questions
- (must be empty before the spec counts as done)
