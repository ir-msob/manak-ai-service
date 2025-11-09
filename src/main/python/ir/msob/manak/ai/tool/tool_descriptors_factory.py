from typing import List, Dict

from src.main.python.ir.msob.manak.ai.tool.model.error_descriptor import ErrorDescriptor
from src.main.python.ir.msob.manak.ai.tool.model.example import Example
from src.main.python.ir.msob.manak.ai.tool.model.parameter_descriptor import ParameterDescriptor
from src.main.python.ir.msob.manak.ai.tool.model.response_descriptor import ResponseDescriptor
from src.main.python.ir.msob.manak.ai.tool.model.response_status import ResponseStatus
from src.main.python.ir.msob.manak.ai.tool.model.tool_descriptor import ToolDescriptor


def get_tool_descriptors() -> List[ToolDescriptor]:
    """Generate tool descriptors for document/repository overview and chunk queries
    using the updated models (ToolDescriptor, ParameterDescriptor, ResponseDescriptor)."""

    # --- Common parameter: tool_id ---
    tool_id_param = ParameterDescriptor(
        type=ParameterDescriptor.ToolParameterType.STRING,
        description="Unique identifier for the tool",
        required=True,
        examples=["documentOverviewQuery"]
    )

    # --- Common error descriptor to attach to tools ---
    generic_error = ErrorDescriptor(
        code="INVALID_REQUEST",
        message="Invalid request parameters or missing required fields.",
        retriable=False,
        resolution="Check and correct input parameters.",
        metadata={}
    )

    # --- Document query input params ---
    doc_query_params: Dict[str, ParameterDescriptor] = {
        "documentIds": ParameterDescriptor(
            type=ParameterDescriptor.ToolParameterType.ARRAY,
            description="Specific document IDs to search within (optional).",
            required=False,
            items=ParameterDescriptor(
                type=ParameterDescriptor.ToolParameterType.STRING,
                description="Document id"
            ),
            examples=[["68fb2324f57252ea71d05a2f"]]
        ),
        "query": ParameterDescriptor(
            type=ParameterDescriptor.ToolParameterType.STRING,
            description="Search query string",
            required=True,
            min_length=1,
            examples=["machine learning algorithms"]
        ),
        "topK": ParameterDescriptor(
            type=ParameterDescriptor.ToolParameterType.NUMBER,
            description="Number of top results to return",
            required=True,
            minimum=1,
            maximum=100,
            examples=[10]
        )
    }

    # --- Document overview item schema ---
    doc_overview_item = ParameterDescriptor(
        type=ParameterDescriptor.ToolParameterType.OBJECT,
        description="Individual document overview result",
        required=True,
        properties={
            "documentId": ParameterDescriptor(
                type=ParameterDescriptor.ToolParameterType.STRING,
                description="Unique identifier for the document",
                required=True,
                examples=["68fb2324f57252ea71d05a2f"]
            ),
            "content": ParameterDescriptor(
                type=ParameterDescriptor.ToolParameterType.STRING,
                description="Summary or overview content of the document",
                required=True,
                examples=["This document covers machine learning fundamentals..."]
            ),
            "meta": ParameterDescriptor(
                type=ParameterDescriptor.ToolParameterType.OBJECT,
                description="Additional metadata about the document",
                required=False,
                examples=[{"author": "John Doe", "created_date": "2024-01-15"}]
            )
        }
    )

    # --- Document overview response schema ---
    doc_overview_response = ParameterDescriptor(
        type=ParameterDescriptor.ToolParameterType.OBJECT,
        description="Complete overview response for document search",
        required=True,
        properties={
            "documentIds": ParameterDescriptor(
                type=ParameterDescriptor.ToolParameterType.ARRAY,
                description="List of document IDs that were searched",
                required=False,
                items=ParameterDescriptor(
                    type=ParameterDescriptor.ToolParameterType.STRING,
                    description="Document ID"
                )
            ),
            "query": ParameterDescriptor(
                type=ParameterDescriptor.ToolParameterType.STRING,
                description="Original search query",
                required=True
            ),
            "topK": ParameterDescriptor(
                type=ParameterDescriptor.ToolParameterType.NUMBER,
                description="Requested number of results",
                required=True
            ),
            "overviews": ParameterDescriptor(
                type=ParameterDescriptor.ToolParameterType.ARRAY,
                description="List of document overviews matching the query",
                required=True,
                items=doc_overview_item
            )
        }
    )

    doc_overview_example = Example(
        title="Document overview example",
        description="Example response for document overview query",
        input={"query": "machine learning algorithms", "topK": 3},
        output={
            "documentIds": ["68fb2324f57252ea71d05a2f"],
            "query": "machine learning algorithms",
            "topK": 3,
            "overviews": [
                {
                    "documentId": "68fb2324f57252ea71d05a2f",
                    "content": "Machine learning overview...",
                    "meta": {"category": "AI"}
                }
            ]
        }
    )

    doc_overview_tool = ToolDescriptor(
        name="Document Overview Query",
        displayName="Document Overview Query",
        category="document",
        version="v1",
        tags=["document", "overview", "search"],
        description="Returns overview data for requested documents based on query parameters.",
        parameters={**doc_query_params, "tool_id": tool_id_param},
        response=ResponseDescriptor(
            statuses=[ResponseStatus(status="200", description="Successful response", contentType="application/json")],
            response_schema=doc_overview_response,
            stream=False,
            examples=[doc_overview_example]
        ),
        examples=[doc_overview_example],
        errors=[generic_error],
        retryPolicy=None,
        timeoutPolicy=None,
        status="ACTIVE"
    )

    # ---------------- Document Chunk Tool ----------------
    doc_chunk_item = ParameterDescriptor(
        type=ParameterDescriptor.ToolParameterType.OBJECT,
        description="Individual document chunk with detailed content",
        required=True,
        properties={
            "documentId": ParameterDescriptor(
                type=ParameterDescriptor.ToolParameterType.STRING,
                description="Unique identifier for the source document",
                required=True
            ),
            "content": ParameterDescriptor(
                type=ParameterDescriptor.ToolParameterType.STRING,
                description="Detailed chunk content from the document",
                required=True
            ),
            "meta": ParameterDescriptor(
                type=ParameterDescriptor.ToolParameterType.OBJECT,
                description="Chunk-specific metadata",
                required=False
            )
        }
    )

    doc_chunk_response = ParameterDescriptor(
        type=ParameterDescriptor.ToolParameterType.OBJECT,
        description="Detailed chunk-level response for document search",
        required=True,
        properties={
            "documentIds": ParameterDescriptor(
                type=ParameterDescriptor.ToolParameterType.ARRAY,
                description="List of document IDs that were searched",
                required=False,
                items=ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.STRING, description="Document ID")
            ),
            "query": ParameterDescriptor(
                type=ParameterDescriptor.ToolParameterType.STRING,
                description="Original search query",
                required=True
            ),
            "topK": ParameterDescriptor(
                type=ParameterDescriptor.ToolParameterType.NUMBER,
                description="Requested number of chunk results",
                required=True
            ),
            "topChunks": ParameterDescriptor(
                type=ParameterDescriptor.ToolParameterType.ARRAY,
                description="List of top matching document chunks",
                required=True,
                items=doc_chunk_item
            ),
            "finalSummary": ParameterDescriptor(
                type=ParameterDescriptor.ToolParameterType.STRING,
                description="Consolidated summary of all top chunks",
                required=False
            )
        }
    )

    doc_chunk_example = Example(
        title="Document chunk example",
        description="Example response for document chunk query",
        input={"query": "neural network applications", "topK": 5},
        output={
            "query": "neural network applications",
            "topK": 5,
            "topChunks": [
                {
                    "documentId": "68fb2324f57252ea71d05a2f",
                    "content": "In this section, we discuss neural networks...",
                    "meta": {"page_number": 5}
                }
            ],
            "finalSummary": "Key applications: image recognition, NLP, predictive analytics."
        }
    )

    doc_chunk_tool = ToolDescriptor(
        name="Document Chunk Query",
        displayName="Document Chunk Query",
        category="document",
        version="v1",
        tags=["document", "chunk", "search"],
        description="Returns detailed chunk-level query results for specified documents.",
        parameters={**doc_query_params, "tool_id": tool_id_param},
        response=ResponseDescriptor(
            statuses=[ResponseStatus(status="200", description="Successful response", contentType="application/json")],
            response_schema=doc_chunk_response,
            stream=False,
            examples=[doc_chunk_example]
        ),
        examples=[doc_chunk_example],
        errors=[generic_error],
        retryPolicy=None,
        timeoutPolicy=None,
        status="ACTIVE"
    )

    # ---------------- Repository Overview Tool ----------------
    repo_query_params: Dict[str, ParameterDescriptor] = {
        "repositoryIds": ParameterDescriptor(
            type=ParameterDescriptor.ToolParameterType.ARRAY,
            description="Specific repository IDs to search within (optional)",
            required=False,
            items=ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.STRING, description="Repository id")
        ),
        "query": ParameterDescriptor(
            type=ParameterDescriptor.ToolParameterType.STRING,
            description="Search query for repository content",
            required=True,
            min_length=1
        ),
        "topK": ParameterDescriptor(
            type=ParameterDescriptor.ToolParameterType.NUMBER,
            description="Number of top results to return",
            required=True,
            minimum=1,
            maximum=100
        )
    }

    repo_overview_item = ParameterDescriptor(
        type=ParameterDescriptor.ToolParameterType.OBJECT,
        description="Individual repository overview result",
        required=True,
        properties={
            "repositoryId": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.STRING,
                                                description="Repository id", required=True),
            "name": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.STRING,
                                        description="Name of repository", required=False),
            "branch": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.STRING, description="Git branch",
                                          required=False),
            "documentId": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.STRING,
                                              description="Document id inside repo", required=False),
            "content": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.STRING,
                                           description="Overview content", required=True),
            "meta": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.OBJECT,
                                        description="Repository metadata", required=False),
            "score": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.NUMBER,
                                         description="Relevance score", required=False, minimum=0.0, maximum=1.0),
            "type": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.STRING,
                                        description="Type of the result", required=False, enum_values=["overview"])
        }
    )

    repo_overview_response = ParameterDescriptor(
        type=ParameterDescriptor.ToolParameterType.OBJECT,
        description="Complete overview response for repository search",
        required=True,
        properties={
            "repositoryIds": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.ARRAY,
                                                 description="List of repository IDs", items=ParameterDescriptor(
                    type=ParameterDescriptor.ToolParameterType.STRING, description="Repository ID")),
            "query": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.STRING,
                                         description="Original search query", required=True),
            "topK": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.NUMBER,
                                        description="Requested number of results", required=True),
            "overviews": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.ARRAY,
                                             description="List of repository overviews", required=True,
                                             items=repo_overview_item)
        }
    )

    repo_overview_example = Example(
        title="Repository overview example",
        description="Example repository overview response",
        input={"query": "authentication middleware", "topK": 5},
        output={
            "query": "authentication middleware",
            "topK": 5,
            "overviews": [
                {
                    "repositoryId": "68fb2324f57252ea71d05a2f",
                    "name": "backend-service",
                    "branch": "main",
                    "content": "Authentication middleware for handling JWT tokens.",
                    "meta": {"language": "python"}
                }
            ]
        }
    )

    repo_overview_tool = ToolDescriptor(
        name="Repository Overview Query",
        displayName="Repository Overview Query",
        category="repository",
        version="v1",
        tags=["repository", "overview", "search"],
        description="Fetches summarized information about repositories based on a search query.",
        parameters={**repo_query_params, "tool_id": tool_id_param},
        response=ResponseDescriptor(
            statuses=[ResponseStatus(status="200", description="Successful response", contentType="application/json")],
            response_schema=repo_overview_response,
            stream=False,
            examples=[repo_overview_example]
        ),
        examples=[repo_overview_example],
        errors=[generic_error],
        retryPolicy=None,
        timeoutPolicy=None,
        status="ACTIVE"
    )

    # ---------------- Repository Chunk Tool ----------------
    repo_chunk_item = ParameterDescriptor(
        type=ParameterDescriptor.ToolParameterType.OBJECT,
        description="Individual repository chunk with file and position details",
        required=True,
        properties={
            "repositoryId": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.STRING,
                                                description="Repository id", required=True),
            "name": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.STRING,
                                        description="Repository name", required=False),
            "branch": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.STRING, description="Git branch",
                                          required=False),
            "documentId": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.STRING,
                                              description="Document id inside repo", required=False),
            "content": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.STRING,
                                           description="Code/content chunk", required=True),
            "meta": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.OBJECT, description="Chunk metadata",
                                        required=False),
            "score": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.NUMBER,
                                         description="Relevance score", required=False, minimum=0.0, maximum=1.0),
            "filePath": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.STRING,
                                            description="Full file path", required=False),
            "fileName": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.STRING, description="File name",
                                            required=False),
            "chunkIndex": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.NUMBER,
                                              description="Index of chunk inside file", required=False, minimum=0),
            "totalChunks": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.NUMBER,
                                               description="Total chunks in file", required=False, minimum=1),
            "type": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.STRING, description="Type of result",
                                        required=False, enum_values=["chunk"])
        }
    )

    repo_chunk_response = ParameterDescriptor(
        type=ParameterDescriptor.ToolParameterType.OBJECT,
        description="Detailed chunk-level response for repository search",
        required=True,
        properties={
            "repositoryIds": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.ARRAY,
                                                 description="List of repo IDs", items=ParameterDescriptor(
                    type=ParameterDescriptor.ToolParameterType.STRING, description="Repository ID")),
            "query": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.STRING,
                                         description="Original search query", required=True),
            "topK": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.NUMBER,
                                        description="Requested number of chunk results", required=True),
            "topChunks": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.ARRAY,
                                             description="List of top matching repository chunks", required=True,
                                             items=repo_chunk_item),
            "finalSummary": ParameterDescriptor(type=ParameterDescriptor.ToolParameterType.STRING,
                                                description="Consolidated summary", required=False)
        }
    )

    repo_chunk_example = Example(
        title="Repository chunk example",
        description="Example repository chunk response",
        input={"query": "JWT authentication middleware", "topK": 5},
        output={
            "query": "JWT authentication middleware",
            "topK": 5,
            "topChunks": [
                {
                    "repositoryId": "68fb2324f57252ea71d05a2f",
                    "filePath": "src/auth/middleware.py",
                    "content": "def authenticate_user(token: str): ..."
                }
            ],
            "finalSummary": "Found multiple JWT implementations across repos."
        }
    )

    repo_chunk_tool = ToolDescriptor(
        name="Repository Chunk Query",
        displayName="Repository Chunk Query",
        category="repository",
        version="v1",
        tags=["repository", "chunk", "search"],
        description="Retrieves chunk-level analysis results for the given repositories.",
        parameters={**repo_query_params, "tool_id": tool_id_param},
        response=ResponseDescriptor(
            statuses=[ResponseStatus(status="200", description="Successful response", contentType="application/json")],
            response_schema=repo_chunk_response,
            stream=False,
            examples=[repo_chunk_example]
        ),
        examples=[repo_chunk_example],
        errors=[generic_error],
        retryPolicy=None,
        timeoutPolicy=None,
        status="ACTIVE"
    )

    return [
        doc_overview_tool,
        doc_chunk_tool,
        repo_overview_tool,
        repo_chunk_tool
    ]
