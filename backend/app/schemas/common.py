from pydantic import BaseModel, ConfigDict


class CamelModel(BaseModel):
    """API payloads are camelCase; the Python side stays snake_case."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda name: name.split("_")[0]
        + "".join(part.title() for part in name.split("_")[1:]),
        ser_json_by_alias=True,
    )
