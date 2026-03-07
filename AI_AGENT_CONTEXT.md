# AI Agent Context — prompts.chat

This file provides the operational context for AI agents working on this repository.
It includes project overview, architecture, coding rules, development workflow, and persistent state tracking.

Agents should read this file before making any modifications.

---

# Project Overview

**prompts.chat** is a social platform where users share and discover AI prompts.

Core capabilities:

* create prompts
* browse prompts
* save prompts to collections
* favorite prompts
* manage user accounts
* admin moderation

Primary goal: enable discovery and reuse of high-quality AI prompts.

---

# Technology Stack

Frontend

* Next.js 16 (App Router)
* React 19
* TypeScript

Backend

* Next.js API routes

Database

* PostgreSQL
* Prisma ORM

Authentication

* NextAuth

Styling

* TailwindCSS
* shadcn/ui

Forms

* React Hook Form
* Zod validation

Internationalization

* next-intl

---

# Development Environment

Requirements

Node >= 20
npm >= 10
PostgreSQL

Install dependencies

npm install

Start development server

npm run dev

Application URL

http://localhost:3000

---

# Database Operations

Run migrations

npm run db:migrate

Push schema (development only)

npm run db:push

Open Prisma Studio

npm run db:studio

Seed development data

npm run db:seed

---

# Type Checking

npx tsc --noEmit

All code must pass type checking before merging.

---

# Key Files

prompts.config.ts
Main application configuration

prisma/schema.prisma
Database schema

src/lib/db.ts
Prisma client singleton

src/lib/auth/index.ts
NextAuth configuration

messages/*.json
Translation files

---

# Project Structure

src/

app/

* (auth)
* api
* prompts
* admin

components/

* ui
* prompts

lib/

* ai
* auth
* plugins

---

# Architecture

System flow

User
→ React Components
→ Next.js API Routes
→ Prisma ORM
→ PostgreSQL

Server Components are preferred by default.

---

# Prompt Data Model

A prompt contains:

title
description
content
tags
author
createdAt

Users can

* create prompts
* edit prompts
* browse prompts
* favorite prompts
* add prompts to collections

---

# Authentication

Authentication is handled by NextAuth.

Responsibilities

* login
* session handling
* user identity

Auth logic location

src/lib/auth

---

# Coding Rules

Default component type

Server Components

Use `"use client"` only when required:

* React state
* event handlers
* browser APIs

---

# UI Rules

Always use components from

src/components/ui

Do not recreate base UI primitives.

Prefer composition over duplication.

---

# Styling

Use TailwindCSS.

Conditional classes should use:

cn()

Avoid custom CSS files unless required.

---

# Translation Rules

All user-visible text must support internationalization.

Server usage

getTranslations()

Client usage

useTranslations()

Never hardcode UI text.

---

# Forms

Standard form stack

React Hook Form
Zod validation

Do not introduce other form libraries.

---

# Database Rules

Prisma client must always be imported from

@/lib/db

Never create additional Prisma instances.

---

# API Design Rules

API routes must

* validate input
* return typed responses
* handle errors explicitly

Responses should be predictable and documented.

---

# Development Workflow

When implementing a feature

1. Update Prisma schema if needed
2. Run database migration
3. Implement API route
4. Implement server logic
5. Build UI components
6. Add translations
7. Test locally
8. Run lint and type check

---

# Performance Guidelines

Prefer

Server Components

Minimize client-side JavaScript.

Only move logic to client components when necessary.

---

# Security Rules

Never commit

.env files
API keys
database credentials
tokens

Secrets must be stored in environment variables.

---

# Anti-Patterns

Avoid

duplicating UI components
bypassing Prisma client
hardcoding translations
creating unnecessary client components
committing secrets

---

# Pre-Commit Checklist

Before committing

Run

npm run lint

and

npx tsc --noEmit

Verify

* no lint errors
* no TypeScript errors
* translations added
* no secrets committed

---

# Agent Priorities

When modifying code follow this priority order

1. Security
2. Database integrity
3. Type safety
4. UI consistency
5. Performance

Higher priority rules must never be violated.

---

# Project State

This section can be updated by agents to track progress.

Current development status

* core prompt system implemented
* authentication configured
* UI components partially complete

Known areas needing improvement

* prompt discovery algorithms
* prompt tagging UX
* search and filtering

---

# Task Queue

Tasks agents may implement

High priority

* improve prompt search
* implement prompt collections
* optimize prompt listing performance

Medium priority

* add prompt rating system
* improve admin moderation tools

Low priority

* UI polish
* performance micro-optimizations

Agents should select tasks from this list when contributing.

---

# Decision Log

This section records important architectural decisions.

Example entries

Decision: Use Prisma ORM
Reason: type safety and schema migrations.

Decision: Use Server Components by default
Reason: performance and reduced client JavaScript.

Decision: Use TailwindCSS + shadcn/ui
Reason: consistent design system.

Agents should append new decisions here when introducing major architectural changes.

---

# Glossary

Prompt
An instruction template designed for use with AI models.

Collection
A group of prompts saved by a user.

Favorite
A bookmarked prompt.

Agent
An AI system assisting development in this repository.
