---
name: subagent-driven-development
description: Use when executing implementation plans with independent tasks in the current session
---

# Subagent-Driven Development

Execute plan by dispatching fresh subagent per task, with two-stage review after each: spec compliance review first, then code quality review.

**Core principle:** Fresh subagent per task + two-stage review (spec then quality) = high quality, fast iteration

## When to Use

**Use when:**
- Have implementation plan with mostly independent tasks
- Want to stay in this session (no context switch)

**vs. Executing Plans (parallel session):**
- Same session (no context switch)
- Fresh subagent per task (no context pollution)
- Two-stage review after each task
- Faster iteration (no human-in-loop between tasks)

## The Process

### 1. Setup
- Read plan file once, extract all tasks with full text
- Note context (where each task fits, dependencies)
- Create todo list with all tasks

### 2. Per Task Loop

**Dispatch Implementer Subagent:**
- Use task tool with `agent_type: "general-purpose"`
- Provide FULL task text and context (don't make subagent read file)
- Subagent implements, tests, commits, self-reviews

**If Implementer Asks Questions:**
- Answer clearly and completely
- Provide additional context if needed
- Don't rush into implementation

**Dispatch Spec Reviewer Subagent:**
- Verify implementation matches specification
- Check for missing requirements and extra/unneeded work
- If issues found → implementer fixes → re-review

**Dispatch Code Quality Reviewer Subagent:**
- Only after spec compliance passes
- Review code quality, testing, maintainability
- If issues found → implementer fixes → re-review

**Mark Task Complete:**
- Only after both reviews pass

### 3. Completion

After all tasks:
- Dispatch final code reviewer for entire implementation
- Use finishing-a-development-branch skill

## Subagent Prompts

### Implementer Prompt Template

```
Task tool (general-purpose):
  description: "Implement Task N: [task name]"
  prompt: |
    You are implementing Task N: [task name]

    ## Task Description
    [FULL TEXT of task from plan]

    ## Context
    [Where this fits, dependencies, architectural context]

    ## Before You Begin
    If you have questions about requirements, approach, or anything unclear - ask now.

    ## Your Job
    1. Implement exactly what the task specifies
    2. Write tests (following TDD)
    3. Verify implementation works
    4. Commit your work
    5. Self-review for completeness and quality
    6. Report back
```

### Spec Reviewer Prompt Template

```
Task tool (general-purpose):
  description: "Review spec compliance for Task N"
  prompt: |
    Review whether implementation matches specification.

    ## What Was Requested
    [FULL TEXT of task requirements]

    ## What Implementer Claims They Built
    [From implementer's report]

    ## Your Job
    Read the implementation code and verify:
    - Did they implement everything requested?
    - Did they build things that weren't requested?
    - Any misunderstandings of requirements?

    Report: ✅ Spec compliant OR ❌ Issues found: [list]
```

### Code Quality Reviewer Prompt Template

```
Task tool (code-review):
  description: "Code quality review for Task N"
  prompt: |
    Review code quality for [what was implemented].
    Base SHA: [commit before task]
    Head SHA: [current commit]

    Focus on: code cleanliness, test quality, maintainability
```

## Red Flags

**Never:**
- Start implementation on main/master branch without consent
- Skip reviews (spec compliance OR code quality)
- Proceed with unfixed issues
- Make subagent read plan file (provide full text)
- Start code quality review before spec compliance passes
- Move to next task while reviews have open issues

**If subagent fails task:**
- Dispatch fix subagent with specific instructions
- Don't try to fix manually (context pollution)

## Integration

**Required workflow skills:**
- **using-git-worktrees** - Set up isolated workspace before starting
- **writing-plans** - Creates the plan this skill executes
- **requesting-code-review** - Template for reviewer subagents
- **finishing-a-development-branch** - Complete development after all tasks
- **test-driven-development** - Subagents follow TDD for each task
