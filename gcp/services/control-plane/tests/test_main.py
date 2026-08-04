from unittest.mock import patch

from platform_api.__main__ import main


def test_main_runs_uvicorn_factory() -> None:
    with patch("platform_api.__main__.uvicorn.run") as run:
        main()

    run.assert_called_once_with(
        "platform_api.api.app:create_app",
        factory=True,
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
