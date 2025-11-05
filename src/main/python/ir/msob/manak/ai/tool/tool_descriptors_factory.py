from typing import List

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
        examples=["documentOverviewQuery", "repositoryChunkQuery"]
    )

    error_param = ToolParameter(
        type=ToolParameter.ToolParameterType.STRING,
        description="Error message if operation fails",
        required=False,
        examples=["Invalid query parameter", "Document not found"]
    )

    # -----------------------
    # Document Query Request Parameter
    # -----------------------
    doc_query_request_param = ToolParameter(
        type=ToolParameter.ToolParameterType.OBJECT,
        description="Query parameters for searching documents",
        required=True,
        properties={
            "document_ids": ToolParameter(
                type=ToolParameter.ToolParameterType.ARRAY,
                description="Specific document IDs to search within (optional)",
                required=False,
                items=ToolParameter(
                    type=ToolParameter.ToolParameterType.STRING,
                    description="Unique document identifier",
                    examples=["doc_12345", "doc_67890"]
                ),
                examples=[["doc_12345", "doc_67890"]]
            ),
            "query": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Search query string",
                required=True,
                examples=["machine learning algorithms", "python programming basics"],
                min_length=1
            ),
            "top_k": ToolParameter(
                type=ToolParameter.ToolParameterType.NUMBER,
                description="Number of top results to return",
                required=True,
                examples=[5, 10, 20],
                minimum=1,
                maximum=100
            )
        }
    )

    # -----------------------
    # Document Overview Response Items
    # -----------------------
    doc_overview_item_param = ToolParameter(
        type=ToolParameter.ToolParameterType.OBJECT,
        description="Individual document overview result",
        required=True,
        properties={
            "document_id": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Unique identifier for the document",
                required=True,
                examples=["doc_12345", "doc_67890"]
            ),
            "content": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Summary or overview content of the document",
                required=True,
                examples=[
                    "This document covers machine learning fundamentals including supervised and unsupervised learning approaches."]
            ),
            "meta": ToolParameter(
                type=ToolParameter.ToolParameterType.OBJECT,
                description="Additional metadata about the document",
                required=False,
                examples=[{"author": "John Doe", "created_date": "2024-01-15", "category": "technical"}]
            )
        }
    )

    doc_overview_response_param = ToolParameter(
        type=ToolParameter.ToolParameterType.OBJECT,
        description="Complete overview response for document search",
        required=True,
        properties={
            "document_ids": ToolParameter(
                type=ToolParameter.ToolParameterType.ARRAY,
                description="List of document IDs that were searched",
                required=False,
                items=ToolParameter(
                    type=ToolParameter.ToolParameterType.STRING,
                    description="Document ID",
                    examples=["doc_12345", "doc_67890"]
                )
            ),
            "query": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Original search query",
                required=True,
                examples=["machine learning algorithms"]
            ),
            "top_k": ToolParameter(
                type=ToolParameter.ToolParameterType.NUMBER,
                description="Requested number of results",
                required=True,
                examples=[5, 10]
            ),
            "overviews": ToolParameter(
                type=ToolParameter.ToolParameterType.ARRAY,
                description="List of document overviews matching the query",
                required=True,
                items=doc_overview_item_param,
                examples=[[
                    {
                        "document_id": "doc_12345",
                        "content": "Machine learning overview...",
                        "meta": {"category": "AI"}
                    }
                ]]
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
            params={"queryRequest": doc_query_request_param}
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
            "document_id": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Unique identifier for the source document",
                required=True,
                examples=["doc_12345", "doc_67890"]
            ),
            "content": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Detailed chunk content from the document",
                required=True,
                examples=["In this section, we discuss neural networks and their applications in computer vision."]
            ),
            "meta": ToolParameter(
                type=ToolParameter.ToolParameterType.OBJECT,
                description="Chunk-specific metadata",
                required=False,
                examples=[{"page_number": 5, "section": "neural_networks", "word_count": 250}]
            )
        }
    )

    doc_chunk_response_param = ToolParameter(
        type=ToolParameter.ToolParameterType.OBJECT,
        description="Detailed chunk-level response for document search",
        required=True,
        properties={
            "document_ids": ToolParameter(
                type=ToolParameter.ToolParameterType.ARRAY,
                description="List of document IDs that were searched",
                required=False,
                items=ToolParameter(
                    type=ToolParameter.ToolParameterType.STRING,
                    description="Document ID",
                    examples=["doc_12345", "doc_67890"]
                )
            ),
            "query": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Original search query",
                required=True,
                examples=["neural network applications"]
            ),
            "top_k": ToolParameter(
                type=ToolParameter.ToolParameterType.NUMBER,
                description="Requested number of chunk results",
                required=True,
                examples=[5, 10]
            ),
            "top_chunks": ToolParameter(
                type=ToolParameter.ToolParameterType.ARRAY,
                description="List of top matching document chunks",
                required=True,
                items=doc_chunk_item_param
            ),
            "final_summary": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Consolidated summary of all top chunks",
                required=False,
                examples=[
                    "The search revealed several key applications of neural networks including image recognition, natural language processing, and predictive analytics."]
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
            params={"queryRequest": doc_query_request_param}
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
    repo_query_request_param = ToolParameter(
        type=ToolParameter.ToolParameterType.OBJECT,
        description="Query parameters for searching repositories",
        required=True,
        properties={
            "repository_ids": ToolParameter(
                type=ToolParameter.ToolParameterType.ARRAY,
                description="Specific repository IDs to search within (optional)",
                required=False,
                items=ToolParameter(
                    type=ToolParameter.ToolParameterType.STRING,
                    description="Unique repository identifier",
                    examples=["repo_12345", "repo_67890"]
                ),
                examples=[["repo_12345", "repo_67890"]]
            ),
            "query": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Search query for repository content",
                required=True,
                examples=["authentication middleware", "database connection pool"],
                min_length=1
            ),
            "top_k": ToolParameter(
                type=ToolParameter.ToolParameterType.NUMBER,
                description="Number of top results to return",
                required=True,
                examples=[5, 10, 20],
                minimum=1,
                maximum=100
            )
        }
    )

    # -----------------------
    # Repository Overview Response Items
    # -----------------------
    repo_overview_item_param = ToolParameter(
        type=ToolParameter.ToolParameterType.OBJECT,
        description="Individual repository overview result",
        required=True,
        properties={
            "repository_id": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Unique identifier for the repository",
                required=True,
                examples=["repo_12345", "repo_67890"]
            ),
            "name": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Name of the repository",
                required=False,
                examples=["backend-service", "frontend-app", "data-pipeline"]
            ),
            "branch": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Git branch name of the repository",
                required=False,
                examples=["main", "develop", "feature/auth-implementation"]
            ),
            "document_id": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Unique identifier for the document within repository",
                required=False,
                examples=["src/auth/middleware.py", "docs/api_spec.md"]
            ),
            "content": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Overview content from the repository",
                required=True,
                examples=["Authentication middleware for handling JWT tokens in API requests."]
            ),
            "meta": ToolParameter(
                type=ToolParameter.ToolParameterType.OBJECT,
                description="Repository and document metadata",
                required=False,
                examples=[{"language": "python", "file_type": "source_code", "last_modified": "2024-01-15"}]
            ),
            "score": ToolParameter(
                type=ToolParameter.ToolParameterType.NUMBER,
                description="Relevance score of the result (0.0 - 1.0)",
                required=False,
                examples=[0.85, 0.92, 0.76],
                minimum=0.0,
                maximum=1.0
            ),
            "type": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Type of the result item",
                required=False,
                examples=["overview"],
                enum_values=["overview"]
            )
        }
    )

    repo_overview_response_param = ToolParameter(
        type=ToolParameter.ToolParameterType.OBJECT,
        description="Complete overview response for repository search",
        required=True,
        properties={
            "repository_ids": ToolParameter(
                type=ToolParameter.ToolParameterType.ARRAY,
                description="List of repository IDs that were searched",
                required=False,
                items=ToolParameter(
                    type=ToolParameter.ToolParameterType.STRING,
                    description="Repository ID",
                    examples=["repo_12345", "repo_67890"]
                )
            ),
            "query": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Original search query",
                required=True,
                examples=["authentication middleware"]
            ),
            "top_k": ToolParameter(
                type=ToolParameter.ToolParameterType.NUMBER,
                description="Requested number of results",
                required=True,
                examples=[5, 10]
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
            params={"queryRequest": repo_query_request_param}
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
            "repository_id": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Unique identifier for the repository",
                required=True,
                examples=["repo_12345", "repo_67890"]
            ),
            "name": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Name of the repository",
                required=False,
                examples=["backend-service", "frontend-app"]
            ),
            "branch": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Git branch name",
                required=False,
                examples=["main", "develop"]
            ),
            "document_id": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Unique identifier for the document",
                required=False,
                examples=["src/auth/middleware.py"]
            ),
            "content": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Detailed code or content chunk",
                required=True,
                examples=[
                    "def authenticate_user(token: str) -> User:\n    # JWT verification logic\n    payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])\n    return User.get(payload['user_id'])"]
            ),
            "meta": ToolParameter(
                type=ToolParameter.ToolParameterType.OBJECT,
                description="Chunk metadata including code-specific information",
                required=False,
                examples=[{"language": "python", "imports": ["jwt", "models"], "function_name": "authenticate_user"}]
            ),
            "score": ToolParameter(
                type=ToolParameter.ToolParameterType.NUMBER,
                description="Relevance score of the chunk",
                required=False,
                examples=[0.85, 0.92],
                minimum=0.0,
                maximum=1.0
            ),
            "file_path": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Full file path within the repository",
                required=False,
                examples=["src/auth/middleware.py", "docs/authentication.md"]
            ),
            "file_name": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Name of the file",
                required=False,
                examples=["middleware.py", "authentication.md"]
            ),
            "chunk_index": ToolParameter(
                type=ToolParameter.ToolParameterType.NUMBER,
                description="Index position of this chunk within the file",
                required=False,
                examples=[0, 1, 2],
                minimum=0
            ),
            "total_chunks": ToolParameter(
                type=ToolParameter.ToolParameterType.NUMBER,
                description="Total number of chunks in the file",
                required=False,
                examples=[5, 10, 15],
                minimum=1
            ),
            "type": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Type of the result",
                required=False,
                examples=["chunk"],
                enum_values=["chunk"]
            )
        }
    )

    repo_chunk_response_param = ToolParameter(
        type=ToolParameter.ToolParameterType.OBJECT,
        description="Detailed chunk-level response for repository search",
        required=True,
        properties={
            "repository_ids": ToolParameter(
                type=ToolParameter.ToolParameterType.ARRAY,
                description="List of repository IDs that were searched",
                required=False,
                items=ToolParameter(
                    type=ToolParameter.ToolParameterType.STRING,
                    description="Repository ID",
                    examples=["repo_12345", "repo_67890"]
                )
            ),
            "query": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Original search query",
                required=True,
                examples=["JWT authentication middleware"]
            ),
            "top_k": ToolParameter(
                type=ToolParameter.ToolParameterType.NUMBER,
                description="Requested number of chunk results",
                required=True,
                examples=[5, 10]
            ),
            "top_chunks": ToolParameter(
                type=ToolParameter.ToolParameterType.ARRAY,
                description="List of top matching repository chunks",
                required=True,
                items=repo_chunk_item_param
            ),
            "final_summary": ToolParameter(
                type=ToolParameter.ToolParameterType.STRING,
                description="Consolidated summary of repository search results",
                required=False,
                examples=[
                    "Found multiple authentication implementations across repositories including JWT middleware, OAuth handlers, and session management utilities."]
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
            params={"queryRequest": repo_query_request_param}
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