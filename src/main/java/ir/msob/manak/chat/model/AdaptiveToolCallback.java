package ir.msob.manak.chat.model;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import ir.msob.jima.core.commons.logger.Logger;
import ir.msob.jima.core.commons.logger.LoggerFactory;
import ir.msob.manak.domain.model.toolhub.dto.InvokeResponse;
import ir.msob.manak.domain.service.toolhub.util.ToolExecutorUtil;
import lombok.SneakyThrows;
import org.springframework.ai.tool.ToolCallback;
import org.springframework.ai.tool.definition.ToolDefinition;
import org.springframework.ai.tool.metadata.ToolMetadata;

import java.time.Instant;
import java.util.Arrays;
import java.util.Collections;
import java.util.Map;

public record AdaptiveToolCallback(ToolDefinition toolDefinition, ToolMetadata toolMetadata,
                                   ToolInvocationAdapter toolInvocationAdapter,
                                   ObjectMapper objectMapper) implements ToolCallback {
    private static final Logger log = LoggerFactory.getLogger(AdaptiveToolCallback.class);

    public AdaptiveToolCallback(ToolDefinition toolDefinition, ToolMetadata toolMetadata,
                                ToolInvocationAdapter toolInvocationAdapter, ObjectMapper objectMapper) {
        this.toolDefinition = toolDefinition;
        this.toolMetadata = toolMetadata;
        this.toolInvocationAdapter = toolInvocationAdapter;
        this.objectMapper = objectMapper;

        log.debug("MyToolCallback initialized for tool: {}", toolDefinition.name());
    }

    @Override
    public ToolDefinition getToolDefinition() {
        return toolDefinition;
    }

    @Override
    public ToolMetadata getToolMetadata() {
        return toolMetadata;
    }

    @SneakyThrows
    @Override
    public String call(String toolInput) {
        log.debug("Tool callback invoked for tool: {} with input: {}", toolDefinition.name(), toolInput);
        Map<String, Object> params = null;
        try {
            // Parse JSON string to Map<String, Object>
            params = parseInput(toolInput);

            // Call tool handler
            Object result = toolInvocationAdapter.handle(params);

            // Convert result to JSON string
            return serializeResult(result);

        } catch (Exception e) {
            log.error("Error in MyToolCallback for tool: {}", toolDefinition.name(), e);
            return createErrorResponse(e, params);
        }
    }

    /**
     * Parse JSON input string to Map<String, Object>
     */
    @SneakyThrows
    private Map<String, Object> parseInput(String toolInput) {
        if (toolInput == null || toolInput.trim().isEmpty()) {
            log.info("Empty input received for tool: {}, using empty parameters", toolDefinition.name());
            return Collections.emptyMap();
        }

        try {
            // Use TypeReference for proper Map<String, Object> deserialization
            Map<String, Object> params = objectMapper.readValue(
                    toolInput,
                    new TypeReference<Map<String, Object>>() {
                    }
            );

            log.debug("Successfully parsed parameters for tool {}: {}", toolDefinition.name(), params);
            return params;

        } catch (Exception e) {
            log.error("Failed to parse tool input for tool {}: {}", toolDefinition.name(), toolInput, e);
            throw new IllegalArgumentException("Invalid JSON input: " + e.getMessage(), e);
        }
    }

    /**
     * Serialize result to JSON string
     */
    @SneakyThrows
    private String serializeResult(Object result) {
        if (result == null) {
            log.info("Tool {} returned null result", toolDefinition.name());
            return "{}";
        }

        try {
            String jsonResult = objectMapper.writeValueAsString(result);
            log.debug("Tool {} execution completed successfully. Result: {}", toolDefinition.name(), jsonResult);
            return jsonResult;

        } catch (Exception e) {
            log.warn("Failed to serialize result for tool {}, using string representation", toolDefinition.name(), e);
            // Fallback: return string representation
            return String.valueOf(result);
        }
    }

    /**
     * Create plain text error response (not JSON)
     */
    private String createErrorResponse(Exception e, Map<String, Object> params) throws JsonProcessingException {
        String toolId = toolDefinition.name();
        String formattedMessage = ToolExecutorUtil.buildErrorResponse(toolId, e);

        InvokeResponse invokeResponse = InvokeResponse.builder()
                .toolId(toolId)
                .error(InvokeResponse.ErrorInfo.builder()
                        .code("EXECUTION_ERROR")
                        .message(formattedMessage)
                        .stackTrace(Arrays.toString(e.getStackTrace()))
                        .details(params)
                        .build())
                .executedAt(Instant.now())
                .build();
        return objectMapper.writeValueAsString(invokeResponse);
    }

    @Override
    public String toString() {
        return "MyToolCallback{tool=" + toolDefinition.name() + "}";
    }
}