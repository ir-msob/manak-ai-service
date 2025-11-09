package ir.msob.manak.chat.model;

import com.fasterxml.jackson.databind.ObjectMapper;
import ir.msob.manak.chat.client.RegistryClient;
import ir.msob.manak.chat.util.RobustSafeParameterCoercer;
import ir.msob.manak.chat.util.ToolSchemaUtil;
import ir.msob.manak.core.model.jima.security.User;
import ir.msob.manak.domain.model.chat.chat.ChatRequestDto;
import ir.msob.manak.domain.model.toolhub.dto.ToolRegistryDto;
import lombok.SneakyThrows;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.tool.ToolCallback;
import org.springframework.ai.tool.definition.DefaultToolDefinition;
import org.springframework.ai.tool.definition.ToolDefinition;
import reactor.core.publisher.Flux;

import java.util.List;

/**
 * Base interface for AI model provider services (e.g., Ollama, OpenAI, etc.)
 * that integrate dynamically registered tools.
 */
public interface ModelProviderService {

    Logger log = LoggerFactory.getLogger(ModelProviderService.class);

    RegistryClient getRegistryClient();

    <CM extends ChatModel> CM getChatModel(String key);

    ToolInvoker getToolInvoker();

    ToolSchemaUtil getToolSchemaUtil();

    ObjectMapper getObjectMapper();

    /**
     * Handles a chat request with dynamic tool registration and streaming response.
     */
    default Flux<String> chat(ChatRequestDto request, User user) {
        log.info("💬 Starting chat for model '{}', message: '{}'", request.getModelSpecificationKey(), request.getMessage());
        return getDynamicTools(request, user)
                .collectList()
                .doOnNext(tools -> log.info("🧩 {} dynamic tools loaded for model '{}'", tools.size(), request.getModelSpecificationKey()))
                .flatMapMany(toolCallbacks -> buildChatClient(request, toolCallbacks))
                .doOnComplete(() -> log.info("✅ Chat session completed for model '{}'", request.getModelSpecificationKey()))
                .doOnError(e -> log.error("❌ Chat session failed for model '{}': {}", request.getModelSpecificationKey(), e.getMessage(), e));
    }

    /**
     * Builds a ChatClient configured with tool callbacks.
     */
    private Flux<String> buildChatClient(ChatRequestDto request, List<ToolCallback> toolCallbacks) {
        log.debug("⚙️ Building ChatClient for model '{}' with {} tools...", request.getModelSpecificationKey(), toolCallbacks.size());

        return ChatClient.create(getChatModel(request.getModelSpecificationKey()))
                .prompt(request.getMessage())
                .toolCallbacks(toolCallbacks)
                .stream()
                .content();
    }

    /**
     * Dynamically loads tool definitions from registry and maps them to callbacks.
     */
    @SneakyThrows
    private Flux<ToolCallback> getDynamicTools(ChatRequestDto request, User user) {
        log.debug("🔍 Fetching available tools from registry...");

        return getRegistryClient().getStream(user)
                .filter(toolDto -> isToolIncluded(toolDto, request.getTools()))
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

        log.debug("🧩 ToolDefinition -> name='{}', desc='{}', schema='{}'", toolDefinition.name(), toolDefinition.description(), toolDefinition.inputSchema());
        return new AdaptiveToolCallback(toolDefinition, metadata, toolInvocationAdapter, getObjectMapper());
    }

    /**
     * Builds a ToolDefinition describing the input schema and description.
     */
    private ToolDefinition createToolDefinition(ToolRegistryDto toolDto) {
        return DefaultToolDefinition.builder()
                .name(toolDto.getToolId())
                .description(toolDto.getDescription())
                .inputSchema(getToolSchemaUtil().toJsonSchema(toolDto.getInputSchema()))
                .build();
    }

    /**
     * Creates tool metadata for error and output schema tracking.
     */
    private ExtendedToolMetadata createToolMetadata(ToolRegistryDto toolDto) {
        return ExtendedToolMetadata.builder()
                .outputSchemaJson(getToolSchemaUtil().toJsonSchema(toolDto.getOutputSchema()))
                .errorSchemaJson(null)
                .build();
    }

    /**
     * Creates a tool handler adapter for invocation routing.
     */
    private ToolInvocationAdapter createToolHandler(ToolRegistryDto toolDto) {
        return new ToolInvocationAdapter(toolDto.getToolId(), getToolInvoker(), toolDto.getInputSchema(), new RobustSafeParameterCoercer(getObjectMapper()));
    }
}