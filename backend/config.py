
import os


def _require(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"Environment variable {name} is not set"
        )

    return value


JWT_SECRET_KEY = _require("JWT_SECRET_KEY")

if len(JWT_SECRET_KEY) < 32:
    raise RuntimeError(
        "JWT_SECRET_KEY must be at least 32 characters long"
    )


JWT_ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)
