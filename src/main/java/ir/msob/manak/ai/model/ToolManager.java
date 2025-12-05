package ir.msob.manak.ai.model;

import com.fasterxml.jackson.databind.ObjectMapper;
import ir.msob.manak.ai.util.RobustSafeParameterCoercer;
import ir.msob.manak.ai.util.ToolSchemaUtil;
import ir.msob.manak.core.model.jima.security.User;
import ir.msob.manak.domain.model.toolhub.dto.ToolRegistryDto;
import ir.msob.manak.domain.service.client.ToolHubClient;
import ir.msob.manak.domain.service.toolhub.ToolInvoker;
import lombok.RequiredArgsConstructor;
import lombok.SneakyThrows;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.tool.ToolCallback;
import org.springframework.ai.tool.definition.DefaultToolDefinition;
import org.springframework.ai.tool.definition.ToolDefinition;
import org.springframework.stereotype.Component;
import reactor.core.publisher.Flux;

import java.util.List;

@Component
@RequiredArgsConstructor
public class ToolManager {

    private static final Logger log = LoggerFactory.getLogger(ToolManager.class);
    private final ToolHubClient toolHubClient;
    private final ToolInvoker toolInvoker;
    private final ToolSchemaUtil toolSchemaUtil;
    private final ObjectMapper objectMapper;

    /**
     * Dynamically loads tool definitions from registry and maps them to callbacks.
     */
    @SneakyThrows
    public Flux<ToolCallback> getDynamicTools(List<String> enabledTools, User user) {
        log.debug("🔍 Fetching available tools from registry...");

        return toolHubClient.getStream(user)
                .filter(toolDto -> isToolIncluded(toolDto, enabledTools))
                .map(this::prepareToolCallback)
                .doOnNext(tool -> log.debug("✅ Registered tool callback for '{}'", tool.getToolDefinition().name()))
                .doOnComplete(() -> log.info("📦 Dynamic tool discovery completed."))
                .doOnError(e -> log.error("❌ Error fetching tools from registry: {}", e.getMessage(), e));
    }

    /**
     * Determines whether a tool should be included based on the request.
     */
    private boolean isToolIncluded(ToolRegistryDto toolDto, List<String> requestedTools) {
        boolean included = requestedTools == null || requestedTools.isEmpty() || requestedTools.contains(toolDto.getToolId());
        log.trace("Tool '{}' inclusion check: {}", toolDto.getToolId(), included);
        return included;
    }

    /**
     * Converts a ToolRegistryDto into a ToolCallback with schema and metadata.
     */
    @SneakyThrows
    private ToolCallback prepareToolCallback(ToolRegistryDto toolDto) {
        log.debug("🛠 Preparing ToolCallback for '{}'", toolDto.getToolId());

        ToolDefinition toolDefinition = createToolDefinition(toolDto);
        ExtendedToolMetadata metadata = createToolMetadata(toolDto);
        ToolInvocationAdapter toolInvocationAdapter = createToolHandler(toolDto);

        log.debug("🧩 ToolDefinition -> name='{}', desc='{}', schema='{}'",
                toolDefinition.name(), toolDefinition.description(), toolDefinition.inputSchema());
        return new AdaptiveToolCallback(toolDefinition, metadata, toolInvocationAdapter, objectMapper);
    }

    /**
     * Builds a ToolDefinition describing the input schema and description.
     */
    private ToolDefinition createToolDefinition(ToolRegistryDto toolDto) {
        return DefaultToolDefinition.builder()
                .name(toolDto.getToolId())
                .description(toolDto.getDescription())
                .inputSchema(toolSchemaUtil.toJsonSchema(toolDto.getInputSchema()))
                .build();
    }

    /**
     * Creates tool metadata for error and output schema tracking.
     */
    private ExtendedToolMetadata createToolMetadata(ToolRegistryDto toolDto) {
        return ExtendedToolMetadata.builder()
                .outputSchemaJson(toolSchemaUtil.toJsonSchema(toolDto.getOutputSchema()))
                .errorSchemaJson(null)
                .build();
    }

    /**
     * Creates a tool handler adapter for invocation routing.
     */
    private ToolInvocationAdapter createToolHandler(ToolRegistryDto toolDto) {
        return new ToolInvocationAdapter(toolDto.getToolId(), toolInvoker, toolDto.getInputSchema(), new RobustSafeParameterCoercer(objectMapper));
    }
}
