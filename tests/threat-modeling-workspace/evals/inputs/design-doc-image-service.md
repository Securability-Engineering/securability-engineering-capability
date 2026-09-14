# Image Processing Service — Design Document

## Overview

The Image Processing Service receives user-uploaded images, transforms them
(resize, crop, watermark), and stores the results in an S3-compatible object
store. A background worker picks up transform jobs from a RabbitMQ queue.
The API is consumed by two clients: a public-facing SPA and an internal
back-office tool.

## Actors

| Actor | Description |
|-------|-------------|
| End user | Authenticated via the platform's OAuth 2.0 IdP; uploads and retrieves their own images. |
| Back-office operator | Staff member; can view and moderate any user's images. Authenticated via the same IdP with an `operator` role claim. |
| Transform worker | Internal service; consumes from the `image-transforms` RabbitMQ queue. |
| CDN | Serves transformed images from the object store; no authentication on read path. |

## Data Classes

- **image-binary** — The raw uploaded file (user content, may contain EXIF with GPS).
- **image-metadata** — Upload timestamp, owner user-id, dimensions, MIME type.
- **transform-job** — Queue message: image key, requested operations, callback URL.
- **moderation-log** — Operator id, action taken, image id, timestamp.

## Architecture

```
[SPA / Back-office] --HTTPS--> [API Gateway] --HTTP--> [Image API (Flask)]
                                                           |
                                                           +--> [PostgreSQL] (metadata)
                                                           +--> [S3] (blobs)
                                                           +--> [RabbitMQ] --> [Transform Worker]
                                                                                  |
                                                                                  +--> [S3]
```

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /images | Upload an image (multipart/form-data) |
| GET  | /images/{id} | Retrieve image metadata |
| GET  | /images/{id}/download | Redirect to a pre-signed S3 URL |
| DELETE | /images/{id} | Soft-delete an image |
| POST | /images/{id}/transform | Enqueue a transform job |
| GET  | /admin/images | List all images (operators only) |
| POST | /admin/images/{id}/moderate | Flag or remove an image |

### Deployment

Single-region Kubernetes deployment. The API and worker are separate pods.
RabbitMQ and PostgreSQL are managed services within the same VPC. S3 is
accessed via HTTPS with IAM role credentials attached to the pods.

### Authentication

All API endpoints require a Bearer token issued by the platform IdP.
The API validates the JWT signature using the IdP's JWKS endpoint, but
the current implementation does not pin the expected algorithm or audience.
Operator endpoints check the `role` claim in the JWT payload.

### Open Questions

- Should EXIF data (especially GPS) be stripped on upload or on transform?
- Is the CDN read path acceptable without per-object access control, or do
  we need signed URLs with short TTLs?
