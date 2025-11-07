package ir.msob.manak.chat.model;

import lombok.Builder;
import org.springframework.ai.tool.metadata.ToolMetadata;

import java.io.Serializable;

/**
 * @param outputSchemaJson JSON schema as string (optional)
 * @param errorSchemaJson  JSON schema as string (optional)
 */
@Builder
public record ExtendedToolMetadata(boolean returnDirect,
                                   String outputSchemaJson,
                                   String errorSchemaJson,
                                   String version) implements ToolMetadata, Serializable {
}
