from uuid import UUID


def convert_str_to_uuid(uuid_str: str) -> UUID:
    return UUID(hex=uuid_str)


def convert_uuid_to_str(uuid: UUID) -> str:
    return uuid.hex
