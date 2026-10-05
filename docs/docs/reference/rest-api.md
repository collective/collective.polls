---
myst:
  html_meta:
    "description": "The @poll and @vote REST API services of collective.polls: requests, responses, errors, and caching."
    "property=og:description": "The @poll and @vote REST API services of collective.polls: requests, responses, errors, and caching."
    "property=og:title": "REST API"
    "keywords": "Plone, polls, REST API, @poll, @vote, plone.restapi"
---

# REST API

The add-on adds two services to every poll.
Both answer the same payload, the state of the poll as the current user sees it.

## Read a poll: `GET @poll`

```http
GET /Plone/a-poll/@poll HTTP/1.1
Accept: application/json
```

It needs the `View` permission on the poll.

```json
{
  "@id": "http://localhost:8080/Plone/a-poll/@poll",
  "uid": "0f2c6e1a9b8d4c3e8f7a6b5c4d3e2f1a",
  "state": "open",
  "allow_anonymous": true,
  "anonymous_blocked": false,
  "show_results": true,
  "results_graph": "bar",
  "options": [
    {"option_id": 0, "description": "Yes"},
    {"option_id": 1, "description": "No"}
  ],
  "max_choices": 1,
  "legend": null,
  "shuffle_options": false,
  "can_vote": true,
  "has_voted": true,
  "total_votes": 3,
  "results": [
    {"option_id": 0, "description": "Yes", "votes": 2, "percentage": 0.6666666666666666},
    {"option_id": 1, "description": "No", "votes": 1, "percentage": 0.3333333333333333}
  ]
}
```

| Key | Type | Description |
|---|---|---|
| `@id` | string | The URL of this service on the poll. |
| `uid` | string | The poll's UID. |
| `state` | string | The workflow state: `private`, `pending`, `open`, or `closed`. |
| `allow_anonymous` | boolean | The poll's setting. |
| `anonymous_blocked` | boolean | `true` for an open poll that allows anonymous votes, when anonymous visitors still cannot vote in it. |
| `show_results` | boolean | The poll's setting. |
| `results_graph` | string | `bar`, `pie`, or `numbers`. |
| `options` | list | The options, in the poll's order. |
| `max_choices` | integer | How many options a voter can pick. |
| `legend` | string or `null` | The poll's legend, `null` when empty. |
| `shuffle_options` | boolean | The poll's setting. The service never shuffles: clients do. |
| `can_vote` | boolean | The current user holds the vote permission on the poll. |
| `has_voted` | boolean or `null` | Whether the current member voted. Always `null` for anonymous callers, see {ref}`rest-caching`. |
| `total_votes` | integer or `null` | Votes so far: one per voter. `null` when the caller may not see the results. |
| `results` | list or `null` | One entry per option: `votes`, and `percentage` as a fraction from 0 to 1 of `total_votes`. `null` when the caller may not see the results. |

The results are part of the answer when one of these is true.

-   The poll is closed.
-   The caller can review the poll.
-   The poll is open and shows partial results, and the caller voted or is anonymous.

## Vote: `POST @vote`

```http
POST /Plone/a-poll/@vote HTTP/1.1
Accept: application/json
Content-Type: application/json

{"option_id": 0}
```

The body holds exactly one of these keys.

| Key | Value |
|---|---|
| `option_id` | One option id. |
| `option_ids` | A list of 1 to `max_choices` distinct option ids. A single choice poll accepts a list of one. |

It needs the `collective.polls: Vote` permission on the poll, which callers have only while the poll is open.
It needs no CSRF token.

On success, it answers `200` with the `@poll` payload, with `has_voted` set to `true` even for an anonymous caller.
An anonymous vote also sets a cookie named `collective.poll.` followed by the poll's UID, which lasts one year and marks the visitor as having voted.

### Errors

The service's own errors answer a body with a type and a message, translated to the request's language.

```json
{"error": {"type": "AlreadyVoted", "message": "You already voted in this poll."}}
```

| Status | Type | When |
|---|---|---|
| `400` | `BadRequest` | The body is not a JSON object with exactly one of `option_id` or `option_ids`, holding integers. |
| `400` | `BadRequest` | An id is not one of the poll's options, a list repeats an id, or it picks more than `max_choices` options. |
| `403` | `AlreadyVoted` | The caller already voted in this poll. |

A caller without the vote permission never reaches the service: the poll is not open, or it does not accept anonymous votes.
`plone.rest` answers `401` to anonymous callers and `403` to members, with its usual error body.

(rest-caching)=

## Caching

| Caller | Service | `Cache-Control` |
|---|---|---|
| Anonymous | `GET @poll` | `max-age=0, s-maxage=120`, with an `ETag` |
| Member | `GET @poll` | `private, no-store` |
| Anyone | `POST @vote` | `private, no-store` |

The answer to anonymous callers is the same for everyone, so shared caches can keep it for two minutes.
It never says whether the caller voted: the client reads the voting cookie instead.
A request with a matching `If-None-Match` header gets `304 Not Modified`.
