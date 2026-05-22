# S2M Process

## Definition

In this repository, **S2M** means **ship to market through revvel-standards**.

If a request is marked S2M, the work must either:

1. use the existing revvel-standard documentation already present in the repository, or
2. create the missing revvel-standard artifacts and deep-research outputs before the work is treated as complete.

## Required Outputs

An S2M-ready deliverable should include:

- a clear `README.md` explaining what the repository does and how to use it now
- `CHANGELOG.md`
- `DEPLOYMENT_GUIDE.md`
- `GO_TO_MARKET.md`
- validation or release checks that confirm the repository is ship-ready
- a documented project analysis covering value, goals, and why the project matters
- a project-management surface in **GitHub Projects**, **Linear**, or both when the request includes project setup

## Deep Research Trigger

Deep research is required when:

- revvel-standard artifacts are missing
- the product thesis is unclear
- the target market, differentiation, or deployment path is not yet documented

## Project Management Rule

When an issue asks to “create a project,” the canonical project name should be recorded in-repo and mirrored into a project-management tool:

- **Preferred title:** `xHumanity`
- **Tooling:** GitHub Projects, Linear, or both
- **Minimum tracking fields:** status, priority, owner, research source, deployment target, and ship gate

## Definition of Done

An S2M issue is done when the repository has:

- the required documentation artifacts
- a validated implementation or release checklist
- a named project-management structure when requested
- enough research context for another operator to continue without re-discovering the standards
