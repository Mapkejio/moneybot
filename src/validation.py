import re

# condition = r"(?<![0-9.a-z])(\d+)(?![0-9.a-z])"
# condition = r"(?<![0-9.a-z])(^\d+((,|\.|_| )\d+)*$)(?![0-9.a-z])"


async def validate(content: str) -> bool:
    if all(char.isdigit() for char in content):
        return True
    return False
