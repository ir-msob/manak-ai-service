from typing import List

from src.main.python.ir.msob.manak.ai.tool.model.request_schema import RequestSchema
from src.main.python.ir.msob.manak.ai.tool.model.response_schema import ResponseSchema
from src.main.python.ir.msob.manak.ai.tool.model.tool_descriptor import ToolDescriptor
from src.main.python.ir.msob.manak.ai.tool.model.tool_parameter import ToolParameter

def get_tool_descriptors() -> List[ToolDescriptor]:
    """Generate a ToolProviderDto containing all document and repository tools."""

    # -----------------------
    # Document Overview Tool
    # -----------------------
    doc_query_param = ToolParameter(
        type="DocumentQueryRequest",
        description="Query parameters for documents",
        required=True
    )
    doc_overview_response_param = ToolParameter(
        type="DocumentOverviewResponse",
        description="Overview response for documents",
        required=True
    )
    doc_overview_tool = ToolDescriptor(
        name="Document Overview Query",
        key="documentOverviewQuery",
        description="Returns overview data for requested documents based on query parameters.",
        input_schema=RequestSchema(tool_id=doc_query_param, params={"queryRequest": doc_query_param}),
        output_schema=ResponseSchema(tool_id=doc_query_param, res={"overviews": doc_overview_response_param}),
        status="ACTIVE"
    )

    # -----------------------
    # Document Chunk Tool
    # -----------------------
    doc_chunk_response_param = ToolParameter(
        type="DocumentChunkResponse",
        description="Chunk-level response for documents",
        required=True
    )
    doc_chunk_tool = ToolDescriptor(
        name="Document Chunk Query",
        key="documentChunkQuery",
        description="Returns detailed chunk-level query results for specified documents.",
        input_schema=RequestSchema(tool_id=doc_query_param, params={"queryRequest": doc_query_param}),
        output_schema=ResponseSchema(tool_id=doc_query_param, res={"topChunks": doc_chunk_response_param}),
        status="ACTIVE"
    )

    # -----------------------
    # Repository Overview Tool
    # -----------------------
    repo_query_param = ToolParameter(
        type="RepositoryQueryRequest",
        description="Query parameters for repositories",
        required=True
    )
    repo_overview_response_param = ToolParameter(
        type="RepositoryOverviewResponse",
        description="Overview response for repositories",
        required=True
    )
    repo_overview_tool = ToolDescriptor(
        name="Repository Overview Query",
        key="repositoryOverviewQuery",
        description="Fetches summarized information about repositories based on a search query.",
        input_schema=RequestSchema(tool_id=repo_query_param, params={"queryRequest": repo_query_param}),
        output_schema=ResponseSchema(tool_id=repo_query_param, res={"overviews": repo_overview_response_param}),
        status="ACTIVE"
    )

    # -----------------------
    # Repository Chunk Tool
    # -----------------------
    repo_chunk_response_param = ToolParameter(
        type="RepositoryChunkResponse",
        description="Chunk-level response for repositories",
        required=True
    )
    repo_chunk_tool = ToolDescriptor(
        name="Repository Chunk Query",
        key="repositoryChunkQuery",
        description="Retrieves chunk-level analysis results for the given repositories.",
        input_schema=RequestSchema(tool_id=repo_query_param, params={"queryRequest": repo_query_param}),
        output_schema=ResponseSchema(tool_id=repo_query_param, res={"top_chunks": repo_chunk_response_param}),
        status="ACTIVE"
    )

    return [
        doc_overview_tool,
        doc_chunk_tool,
        repo_overview_tool,
        repo_chunk_tool
    ]
