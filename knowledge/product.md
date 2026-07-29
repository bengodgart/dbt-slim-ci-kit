---
type: Product
title: dbt-slim-ci-kit
description: Free "Slim CI" for dbt Core. On every pull request it builds and tests **only the models you changed and their descendants**, in a throwaway staging schema, then comments the result on the PR and blocks the merge if anything fails.
domain: Data & Analytics
users: dbt Core teams that do not pay for dbt Cloud and want real CI on pull requests.
lifecycle: shipped
pricing: Free and open source.
generated:
  by: claude-opus-5
  at: '2026-07-29T00:45:00+00:00'
status: stable
resource: https://github.com/bengodgart/dbt-slim-ci-kit.git
---

# dbt-slim-ci-kit

Free "Slim CI" for dbt Core. On every pull request it builds and tests **only the models you changed and their descendants**, in a throwaway staging schema, then comments the result on the PR and blocks the merge if anything fails.

## Who it is for

Analytics engineers running dbt Core with GitHub Actions, who want the Slim CI behaviour dbt Cloud charges for.

## What problem it solves

A full `dbt build` on every pull request is slow enough that teams stop running it. This builds and tests only the models you changed and their descendants, in a throwaway staging schema, comments the result on the pull request, and blocks the merge when anything fails.

## Current state

Shipped and public.
