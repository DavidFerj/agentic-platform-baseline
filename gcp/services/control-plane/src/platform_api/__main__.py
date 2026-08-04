"""Executable entry point for local API development."""

import uvicorn


def main() -> None:
    """Run the API through Uvicorn's application factory."""
    uvicorn.run(
        "platform_api.api.app:create_app",
        factory=True,
        host="0.0.0.0",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    main()
