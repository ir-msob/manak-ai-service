from typing import List, Dict

from src.main.python.ir.msob.manak.ai.tool.model.request_schema import RequestSchema
from src.main.python.ir.msob.manak.ai.tool.model.response_schema import ResponseSchema
from src.main.python.ir.msob.manak.ai.tool.model.tool_descriptor import ToolDescriptor
from src.main.python.ir.msob.manak.ai.tool.model.tool_parameter import ToolParameter


def get_tool_descriptors() -> List[ToolDescriptor]:
    """Generate a ToolProviderDto containing all document and repository tools."""

    # -----------------------
    # Common Basic Parameters
    # -----------------------
    tool_id_param = ToolParameter(
        type=ToolParameter.ToolParameterType.STRING,
        description="Unique identifier for the tool",
        required=True,
        example="documentOverviewQuery"
    )

    error_param = ToolParameter(
        type=ToolParameter.ToolParameterType.STRING,
        description="Error message if operation fails",
        required=False,
        example="Invalid query parameter"
    )

    # -----------------------
    # Document Query Request Parameter
    # -----------------------
    doc_query_request_param: Dict[str, ToolParameter] = {
        "documentIds": ToolParameter(
            type=ToolParameter.ToolParameterType.ARRAY,
            description="Specific document IDs to search within (optional)",
            required=False,
            items=ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Unique document identifier",
                example="68fb2324f57252ea71d05a2f"
            ),
            example="68fb2324f57252ea71d05a2f"
        ),
        "query": ToolParameter(
            type=ToolParameter.ToolParameterType.STRING,
            description="Search query string",
            required=True,
            example="machine learning algorithms",
            min_length=1
        ),
        "topK": ToolParameter(
            type=ToolParameter.ToolParameterType.NUMBER,
            description="Number of top results to return",
            required=True,
            example=10,
            minimum=1,
            maximum=100
        )
    }

    # -----------------------
    # Document Overview Response Items
    # -----------------------
    doc_overview_item_param = ToolParameter(
        type=ToolParameter.ToolParameterType.OBJECT,
        description="Individual document overview result",
        required=True,
        properties={
            "documentId": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Unique identifier for the document",
                required=True,
                example="68fb2324f57252ea71d05a2f"
            ),
            "content": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Summary or overview content of the document",
                required=True,
                example="This document covers machine learning fundamentals including supervised and unsupervised learning approaches."
            ),
            "meta": ToolParameter(
                type=ToolParameter.ToolParameterType.OBJECT,
                description="Additional metadata about the document",
                required=False,
                example={"author": "John Doe", "created_date": "2024-01-15", "category": "technical"}
            )
        }
    )

    doc_overview_response_param = ToolParameter(
        type=ToolParameter.ToolParameterType.OBJECT,
        description="Complete overview response for document search",
        required=True,
        properties={
            "documentIds": ToolParameter(
                type=ToolParameter.ToolParameterType.ARRAY,
                description="List of document IDs that were searched",
                required=False,
                items=ToolParameter(
                    type=ToolParameter.ToolParameterType.STRING,
                    description="Document ID",
                    example="68fb2324f57252ea71d05a2f"
                )
            ),
            "query": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Original search query",
                required=True,
                example="machine learning algorithms"
            ),
            "topK": ToolParameter(
                type=ToolParameter.ToolParameterType.NUMBER,
                description="Requested number of results",
                required=True,
                example=10
            ),
            "overviews": ToolParameter(
                type=ToolParameter.ToolParameterType.ARRAY,
                description="List of document overviews matching the query",
                required=True,
                items=doc_overview_item_param,
                example={
                    "documentId": "68fb2324f57252ea71d05a2f",
                    "content": "Machine learning overview...",
                    "meta": {"category": "AI"}
                }

            )
        }
    )

    # -----------------------
    # Document Overview Tool
    # -----------------------
    doc_overview_tool = ToolDescriptor(
        name="Document Overview Query",
        key="documentOverviewQuery",
        description="Returns overview data for requested documents based on query parameters.",
        input_schema=RequestSchema(
            tool_id=tool_id_param,
            params=doc_query_request_param
        ),
        output_schema=ResponseSchema(
            tool_id=tool_id_param,
            res=doc_overview_response_param,
            error=error_param
        ),
        status="ACTIVE"
    )

    # -----------------------
    # Document Chunk Response Parameter
    # -----------------------
    doc_chunk_item_param = ToolParameter(
        type=ToolParameter.ToolParameterType.OBJECT,
        description="Individual document chunk with detailed content",
        required=True,
        properties={
            "documentId": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Unique identifier for the source document",
                required=True,
                example="68fb2324f57252ea71d05a2f"
            ),
            "content": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Detailed chunk content from the document",
                required=True,
                example="In this section, we discuss neural networks and their applications in computer vision."
            ),
            "meta": ToolParameter(
                type=ToolParameter.ToolParameterType.OBJECT,
                description="Chunk-specific metadata",
                required=False,
                example={"page_number": 5, "section": "neural_networks", "word_count": 250}
            )
        }
    )

    doc_chunk_response_param = ToolParameter(
        type=ToolParameter.ToolParameterType.OBJECT,
        description="Detailed chunk-level response for document search",
        required=True,
        properties={
            "documentIds": ToolParameter(
                type=ToolParameter.ToolParameterType.ARRAY,
                description="List of document IDs that were searched",
                required=False,
                items=ToolParameter(
                    type=ToolParameter.ToolParameterType.STRING,
                    description="Document ID",
                    example="68fb2324f57252ea71d05a2f"
                )
            ),
            "query": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Original search query",
                required=True,
                example="neural network applications"
            ),
            "topK": ToolParameter(
                type=ToolParameter.ToolParameterType.NUMBER,
                description="Requested number of chunk results",
                required=True,
                example=5
            ),
            "topChunks": ToolParameter(
                type=ToolParameter.ToolParameterType.ARRAY,
                description="List of top matching document chunks",
                required=True,
                items=doc_chunk_item_param
            ),
            "finalSummary": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Consolidated summary of all top chunks",
                required=False,
                example="The search revealed several key applications of neural networks including image recognition, natural language processing, and predictive analytics."
            )
        }
    )

    # -----------------------
    # Document Chunk Tool
    # -----------------------
    doc_chunk_tool = ToolDescriptor(
        name="Document Chunk Query",
        key="documentChunkQuery",
        description="Returns detailed chunk-level query results for specified documents.",
        input_schema=RequestSchema(
            tool_id=tool_id_param,
            params=doc_query_request_param
        ),
        output_schema=ResponseSchema(
            tool_id=tool_id_param,
            res=doc_chunk_response_param,
            error=error_param
        ),
        status="ACTIVE"
    )

    # -----------------------
    # Repository Query Request Parameter
    # -----------------------
    repo_query_request_param: Dict[str, ToolParameter] = {
        "repositoryIds": ToolParameter(
            type=ToolParameter.ToolParameterType.ARRAY,
            description="Specific repository IDs to search within (optional)",
            required=False,
            items=ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Unique repository identifier",
                example="68fb2324f57252ea71d05a2f"
            ),
            example="68fb2324f57252ea71d05a2f"
        ),
        "query": ToolParameter(
            type=ToolParameter.ToolParameterType.STRING,
            description="Search query for repository content",
            required=True,
            example="authentication middleware",
            min_length=1
        ),
        "topK": ToolParameter(
            type=ToolParameter.ToolParameterType.NUMBER,
            description="Number of top results to return",
            required=True,
            example=10,
            minimum=1,
            maximum=100
        )
    }

    # -----------------------
    # Repository Overview Response Items
    # -----------------------
    repo_overview_item_param = ToolParameter(
        type=ToolParameter.ToolParameterType.OBJECT,
        description="Individual repository overview result",
        required=True,
        properties={
            "repositoryId": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Unique identifier for the repository",
                required=True,
                example="68fb2324f57252ea71d05a2f"
            ),
            "name": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Name of the repository",
                required=False,
                example="backend-service"
            ),
            "branch": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Git branch name of the repository",
                required=False,
                example="main"
            ),
            "documentId": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Unique identifier for the document within repository",
                required=False,
                example="src/auth/middleware.py"
            ),
            "content": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Overview content from the repository",
                required=True,
                example="Authentication middleware for handling JWT tokens in API requests."
            ),
            "meta": ToolParameter(
                type=ToolParameter.ToolParameterType.OBJECT,
                description="Repository and document metadata",
                required=False,
                example={"language": "python", "file_type": "source_code", "last_modified": "2024-01-15"}
            ),
            "score": ToolParameter(
                type=ToolParameter.ToolParameterType.NUMBER,
                description="Relevance score of the result (0.0 - 1.0)",
                required=False,
                example=0.85,
                minimum=0.0,
                maximum=1.0
            ),
            "type": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Type of the result item",
                required=False,
                example="overview",
                enum_values=["overview"]
            )
        }
    )

    repo_overview_response_param = ToolParameter(
        type=ToolParameter.ToolParameterType.OBJECT,
        description="Complete overview response for repository search",
        required=True,
        properties={
            "repositoryIds": ToolParameter(
                type=ToolParameter.ToolParameterType.ARRAY,
                description="List of repository IDs that were searched",
                required=False,
                items=ToolParameter(
                    type=ToolParameter.ToolParameterType.STRING,
                    description="Repository ID",
                    example="68fb2324f57252ea71d05a2f"
                )
            ),
            "query": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Original search query",
                required=True,
                example="authentication middleware"
            ),
            "topK": ToolParameter(
                type=ToolParameter.ToolParameterType.NUMBER,
                description="Requested number of results",
                required=True,
                example=10
            ),
            "overviews": ToolParameter(
                type=ToolParameter.ToolParameterType.ARRAY,
                description="List of repository overviews matching the query",
                required=True,
                items=repo_overview_item_param
            )
        }
    )

    # -----------------------
    # Repository Overview Tool
    # -----------------------
    repo_overview_tool = ToolDescriptor(
        name="Repository Overview Query",
        key="repositoryOverviewQuery",
        description="Fetches summarized information about repositories based on a search query.",
        input_schema=RequestSchema(
            tool_id=tool_id_param,
            params=repo_query_request_param
        ),
        output_schema=ResponseSchema(
            tool_id=tool_id_param,
            res=repo_overview_response_param,
            error=error_param
        ),
        status="ACTIVE"
    )

    # -----------------------
    # Repository Chunk Response Items
    # -----------------------
    repo_chunk_item_param = ToolParameter(
        type=ToolParameter.ToolParameterType.OBJECT,
        description="Individual repository chunk with file and position details",
        required=True,
        properties={
            "repositoryId": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Unique identifier for the repository",
                required=True,
                example="68fb2324f57252ea71d05a2f"
            ),
            "name": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Name of the repository",
                required=False,
                example="backend-service"
            ),
            "branch": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Git branch name",
                required=False,
                example="main"
            ),
            "documentId": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Unique identifier for the document",
                required=False,
                example="src/auth/middleware.py"
            ),
            "content": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Detailed code or content chunk",
                required=True,
                example="def authenticate_user(token: str) -> User:\n    # JWT verification logic\n    payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])\n    return User.get(payload['user_id'])"
            ),
            "meta": ToolParameter(
                type=ToolParameter.ToolParameterType.OBJECT,
                description="Chunk metadata including code-specific information",
                required=False,
                example={"language": "python", "imports": ["jwt", "models"], "function_name": "authenticate_user"}
            ),
            "score": ToolParameter(
                type=ToolParameter.ToolParameterType.NUMBER,
                description="Relevance score of the chunk",
                required=False,
                example=0.85,
                minimum=0.0,
                maximum=1.0
            ),
            "filePath": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Full file path within the repository",
                required=False,
                example="src/auth/middleware.py"
            ),
            "fileName": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Name of the file",
                required=False,
                example="middleware.py"
            ),
            "chunkIndex": ToolParameter(
                type=ToolParameter.ToolParameterType.NUMBER,
                description="Index position of this chunk within the file",
                required=False,
                example=2,
                minimum=0
            ),
            "totalChunks": ToolParameter(
                type=ToolParameter.ToolParameterType.NUMBER,
                description="Total number of chunks in the file",
                required=False,
                example=15,
                minimum=1
            ),
            "type": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Type of the result",
                required=False,
                example="chunk",
                enum_values=["chunk"]
            )
        }
    )

    repo_chunk_response_param = ToolParameter(
        type=ToolParameter.ToolParameterType.OBJECT,
        description="Detailed chunk-level response for repository search",
        required=True,
        properties={
            "repositoryIds": ToolParameter(
                type=ToolParameter.ToolParameterType.ARRAY,
                description="List of repository IDs that were searched",
                required=False,
                items=ToolParameter(
                    type=ToolParameter.ToolParameterType.STRING,
                    description="Repository ID",
                    example="68fb2324f57252ea71d05a2f"
                )
            ),
            "query": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Original search query",
                required=True,
                example="JWT authentication middleware"
            ),
            "topK": ToolParameter(
                type=ToolParameter.ToolParameterType.NUMBER,
                description="Requested number of chunk results",
                required=True,
                example=10
            ),
            "topChunks": ToolParameter(
                type=ToolParameter.ToolParameterType.ARRAY,
                description="List of top matching repository chunks",
                required=True,
                items=repo_chunk_item_param
            ),
            "finalSummary": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Consolidated summary of repository search results",
                required=False,
                example="Found multiple authentication implementations across repositories including JWT middleware, OAuth handlers, and session management utilities."
            )
        }
    )

    # -----------------------
    # Repository Chunk Tool
    # -----------------------
    repo_chunk_tool = ToolDescriptor(
        name="Repository Chunk Query",
        key="repositoryChunkQuery",
        description="Retrieves chunk-level analysis results for the given repositories.",
        input_schema=RequestSchema(
            tool_id=tool_id_param,
            params=repo_query_request_param
        ),
        output_schema=ResponseSchema(
            tool_id=tool_id_param,
            res=repo_chunk_response_param,
            error=error_param
        ),
        status="ACTIVE"
    )

    return [
        doc_overview_tool,
        doc_chunk_tool,
        repo_overview_tool,
        repo_chunk_tool
    ]
