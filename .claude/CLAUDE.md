# AI Resume Backend Rules

## IMPORTANT

- Read only the minimum required files.
- Do not scan the entire repository unless explicitly requested.
- If a request can be answered in under 100 words, do not exceed 100 words.
- If a request can be answered with a code diff, return only the diff.
- Return only what was requested.
- Do not repeat requirements already present in the conversation.

---

## Response Style

- Be concise.
- Assume I am a senior backend engineer.
- Do not explain basic Python, FastAPI, Redis, MongoDB, Vector Search, LLMs, Prompt Engineering, RAG, Docker, or system design concepts.
- Use bullet points instead of long paragraphs.
- Avoid introductions and conclusions unless necessary.

---

## Repository Access

- Read only files required for the task.
- Do not scan the entire repository unless explicitly requested.
- Do not inspect unrelated files.
- Prefer targeted file reads over broad codebase exploration.
- Before reading additional files, explain why they are needed.

---

## Code Changes

- Return only modified code.
- Never regenerate complete files unless explicitly requested.
- Prefer unified git diff format.
- Preserve existing code style.
- Preserve existing architecture.
- Do not rename variables, functions, classes, files, or folders unless required.
- Do not add comments unless requested.
- Do not perform unrelated refactoring.

---

## Debugging

Always provide:

1. Root Cause
2. Evidence
3. Fix
4. Minimal Patch

When logs, stack traces, prompts, AI outputs, API responses, embeddings, vector search results, Redis data, backend code, or configuration are provided:

- Analyze the provided data first.
- Do not provide generic troubleshooting checklists.
- Rank possible causes by confidence percentage.
- Focus on the highest-confidence cause first.
- Explain why other causes are less likely.

---

## FastAPI

- Follow existing project patterns.
- Prefer dependency injection where already used.
- Keep endpoints thin.
- Keep business logic in services.
- Keep AI orchestration separated from API routes.
- Avoid unnecessary abstractions.
- Preserve backward compatibility.

---

## MongoDB

- Identify query bottlenecks before suggesting changes.
- Consider index usage before code changes.
- Explain expected performance impact.
- Avoid theoretical optimizations.
- Consider collection growth.
- Suggest indexes only when justified by query patterns.

---

## Redis & Semantic Search

- Consider cache invalidation.
- Consider TTL behavior.
- Avoid unnecessary cache writes.
- Reuse existing embedding storage patterns.
- Optimize vector retrieval before adding new logic.
- Consider embedding generation cost.
- Consider Redis memory impact.
- Minimize duplicate embeddings.

---

## AI Features

This backend powers:

- Resume Analysis
- Resume Optimization
- Targeted Resume Generation
- LinkedIn Profile Optimization
- AI Career Recommendations
- Future AI-driven career tools

When working on AI features:

- Prioritize output quality.
- Prioritize prompt consistency.
- Minimize token consumption.
- Reduce API calls whenever possible.
- Reuse existing context and embeddings.
- Prefer deterministic outputs when appropriate.
- Preserve existing prompt structures unless improvement is justified.

---

## Gemini API

When modifying Gemini integrations:

- Consider token cost.
- Consider latency.
- Consider rate limits.
- Consider response consistency.
- Consider retry behavior.
- Consider fallback handling.
- Avoid unnecessary model calls.
- Reuse cached AI responses when appropriate.

---

## Prompt Engineering

When improving prompts:

- Make the smallest effective change.
- Preserve output schema.
- Preserve downstream compatibility.
- Avoid prompt bloat.
- Prefer structured outputs.
- Prefer JSON responses when consumed by code.
- Minimize prompt tokens.

---

## AI Evaluation

For AI-generated outputs:

- Focus on accuracy.
- Focus on actionability.
- Avoid generic career advice.
- Prefer measurable recommendations.
- Optimize for recruiter relevance.
- Optimize for ATS compatibility.
- Optimize for user value.

---

## Architecture

Provide:

1. Recommendation
2. Pros
3. Cons
4. Complexity

Avoid discussing multiple alternatives unless requested.

---

## Performance

- Suggest optimizations only when relevant.
- Highlight AI latency bottlenecks.
- Highlight token cost bottlenecks.
- Highlight embedding generation bottlenecks.
- Highlight Redis memory bottlenecks.
- Highlight MongoDB bottlenecks when detected.

---

## Context Management

- Summarize long discussions instead of repeating them.
- Do not restate code already shown.
- Do not generate examples unless requested.
- Do not provide multiple solutions unless requested.
- Prefer the most likely solution first.

---

## AI Cost Optimization

Always consider:

- Gemini token usage
- Embedding generation cost
- Redis memory usage
- Duplicate AI requests
- Cache opportunities
- Prompt size reduction
- Retrieval optimization

Prefer solutions that reduce operational cost without reducing output quality.
