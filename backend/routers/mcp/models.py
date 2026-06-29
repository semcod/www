from pydantic import BaseModel, Field


class MCPResource(BaseModel):
    """MCP Resource definition."""

    uri: str
    name: str
    description: str
    mime_type: str = "application/json"


class MCPTool(BaseModel):
    """MCP Tool definition."""

    name: str
    description: str
    input_schema: dict


class MCPResourceResponse(BaseModel):
    """MCP resource content response."""

    uri: str
    mime_type: str
    content: dict


class MCPToolRequest(BaseModel):
    """MCP tool invocation request."""

    name: str
    arguments: dict = Field(default_factory=dict)
