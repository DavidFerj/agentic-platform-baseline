# GCP backend

This directory contains every Google Cloud/Firebase deployable and its platform
configuration. Deployment boundaries follow runtime behavior, not individual classes or
internal helper services.

| Directory         | Deployment model                         | Use when                                                 |
| ----------------- | ---------------------------------------- | -------------------------------------------------------- |
| `services/`       | Cloud Run service                        | Cohesive HTTP API or long-lived orchestration capability |
| `functions/`      | Cloud Run function                       | Narrow HTTP/CloudEvent adapter with one entry point      |
| `jobs/`           | Cloud Run job                            | Finite, retryable work that exits                        |
| `firebase/`       | Managed BaaS configuration               | Firestore rules/indexes and emulator tests               |
| `packages/`       | Build-time shared contracts/libraries    | Stable reuse with explicit consumers                     |
| `infrastructure/` | Terraform, containers, and observability | Reproducible platform configuration                      |

A new deployable requires evidence of independent scaling, lifecycle, ownership,
security isolation, or runtime behavior. A new Python module does not require a new
Cloud Run resource.
