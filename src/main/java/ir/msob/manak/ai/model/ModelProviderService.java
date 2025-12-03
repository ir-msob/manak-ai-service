package ir.msob.manak.ai.model;

import com.fasterxml.jackson.databind.ObjectMapper;
import ir.msob.manak.ai.util.RobustSafeParameterCoercer;
import ir.msob.manak.ai.util.ToolSchemaUtil;
import ir.msob.manak.core.model.jima.security.User;
import ir.msob.manak.domain.model.ai.chat.ChatRequestDto;
import ir.msob.manak.domain.model.ai.chat.ChatRequestDto.Message;
import ir.msob.manak.domain.model.ai.chat.ChatRequestDto.TemplateRef;
import ir.msob.manak.domain.model.ai.embedding.EmbeddingRequestDto;
import ir.msob.manak.domain.model.ai.embedding.EmbeddingResponseDto;
import ir.msob.manak.domain.model.toolhub.dto.ToolRegistryDto;
import ir.msob.manak.domain.service.client.ToolHubClient;
import ir.msob.manak.domain.service.toolhub.ToolInvoker;
import lombok.SneakyThrows;
import org.apache.logging.log4j.util.Strings;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.messages.AssistantMessage;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.chat.prompt.DefaultChatOptions;
import org.springframework.ai.embedding.*;
import org.springframework.ai.template.st.StTemplateRenderer;
import org.springframework.ai.tool.ToolCallback;
import org.springframework.ai.tool.definition.DefaultToolDefinition;
import org.springframework.ai.tool.definition.ToolDefinition;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.List;
import java.util.Map;
import java.util.Objects;

/**
 * Base interface for AI model provider services (e.g., Ollama, OpenAI, etc.)
 * that integrate dynamically registered tools.
 * <p>
 * Adapted to work with the new ChatRequestDto (role-based messages, templates, INLINE/BASE64 content).
 */
public interface ModelProviderService {

    Logger log = LoggerFactory.getLogger(ModelProviderService.class);

    ToolHubClient getToolHubClient();

    <CM extends ChatModel> CM getChatModel(String key);

    <CM extends AbstractEmbeddingModel> CM getEmbeddingModel(String key);

    ToolInvoker getToolInvoker();

    ToolSchemaUtil getToolSchemaUtil();

    ObjectMapper getObjectMapper();

    /**
     * Handles a chat request with dynamic tool registration and streaming response.
     */
    default Flux<String> chat(ChatRequestDto request, User user) {
        log.info("💬 Starting chat for model '{}', simpleMessage='{}', requestId='{}'",
                request == null ? "null" : request.getModel(),
                request == null ? null : request.getSimpleMessage(),
                request == null ? null : request.getRequestId());

        Flux<ToolCallback> toolCallbacksFlux = request != null && request.isToolsEnabled() ?
                getDynamicTools(request, user) :
                Flux.empty();

        return toolCallbacksFlux
                .collectList()
                .doOnNext(tools -> log.info("🧩 {} dynamic tools loaded for model '{}'", tools.size(), request.getModel()))
                .flatMapMany(toolCallbacks -> buildChatClient(request, toolCallbacks))
                .doOnComplete(() -> log.info("✅ Chat session completed for model '{}', requestId='{}'",
                        request == null ? "null" : request.getModel(),
                        request == null ? null : request.getRequestId()))
                .doOnError(e -> log.error("❌ Chat session failed for model '{}', requestId='{}': {}",
                        request == null ? "null" : request.getModel(),
                        request == null ? null : request.getRequestId(),
                        e.getMessage(), e));
    }

    /**
     * Builds a ChatClient configured with tool callbacks and role-based messages.
     */
    private Flux<String> buildChatClient(ChatRequestDto request, List<ToolCallback> toolCallbacks) {
        Objects.requireNonNull(request, "ChatRequestDto must not be null");
        log.debug("⚙️ Building ChatClient for model '{}' (requestId='{}') with {} tools...",
                request.getModel(), request.getRequestId(), toolCallbacks.size());

        // create spec with empty prompt; we'll populate roles explicitly
        var spec = ChatClient.create(getChatModel(request.getModel()))
                .prompt("")
                .templateRenderer(StTemplateRenderer.builder().build());

        if (!toolCallbacks.isEmpty()) {
            spec.toolCallbacks(toolCallbacks);
        }

        // template variables (may be null)
        Map<String, Object> vars = request.getTemplateVariables() == null ? Map.of() : request.getTemplateVariables();

        // 1) apply templates (SYSTEM / USER / DEVELOPER) if present
        Map<ChatRequestDto.Role, TemplateRef> templates = request.getTemplates();
        if (templates != null && !templates.isEmpty()) {
            // system template
            if (templates.containsKey(ChatRequestDto.Role.SYSTEM)) {
                String systemTemplate = resolveTemplate(templates.get(ChatRequestDto.Role.SYSTEM));
                spec.system(promptSystemSpec -> promptSystemSpec.text(systemTemplate).params(vars));
                log.debug("Added system template message.");
            }
            // assistant template
            if (templates.containsKey(ChatRequestDto.Role.ASSISTANT)) {
                String assistantTemplate = resolveTemplate(templates.get(ChatRequestDto.Role.ASSISTANT));
                spec.messages(new AssistantMessage(assistantTemplate, vars));
                log.debug("Added assistant template message.");
            }
            // user template (if present and no role-based messages)
            if (templates.containsKey(ChatRequestDto.Role.USER)) {
                String userTemplate = resolveTemplate(templates.get(ChatRequestDto.Role.USER));
                spec.user(promptUserSpec -> promptUserSpec.text(userTemplate).params(vars));
                log.debug("Added user template message.");
            }
        }

        // 2) if explicit role-based messages present in request, append them in order (they override simpleMessage)
        if (request.getMessages() != null && !request.getMessages().isEmpty()) {
            for (Message m : request.getMessages()) {
                if (m == null) continue;
                String content = m.getContent();
                ChatRequestDto.Role role = m.getRole() == null ? ChatRequestDto.Role.USER : m.getRole();
                switch (role) {
                    case SYSTEM -> {
                        spec.system(promptSystemSpec -> promptSystemSpec.text(content).params(vars));
                        log.trace("Appended role=SYSTEM message.");
                    }
                    case ASSISTANT -> {
                        spec.messages(new AssistantMessage(content, vars));
                        log.trace("Appended role=ASSISTANT message.");
                    }
                    case USER -> {
                        spec.user(promptUserSpec -> promptUserSpec.text(content).params(vars));
                        log.trace("Appended role=USER message.");
                    }
                }
            }
            log.debug("Added {} role-based messages from request.", request.getMessages().size());
        } else {
            // 3) fallback to simpleMessage if no role messages present and no user template used earlier
            boolean userTemplateUsed = templates != null && templates.containsKey(ChatRequestDto.Role.USER);
            if (!userTemplateUsed && Strings.isNotBlank(request.getSimpleMessage())) {
                spec.user(promptUserSpec -> promptUserSpec.text(request.getSimpleMessage()).params(vars));
                log.debug("Added fallback simpleMessage as user message.");
            }
        }

        // 4) (Optional) map ModelOptions -> provider ChatOptions
        if (request.getOptions() != null) {
            DefaultChatOptions chatOptions = new DefaultChatOptions();
            chatOptions.setModel(request.getModel());

            if (request.getOptions().getTemperature() != null)
                chatOptions.setTemperature(request.getOptions().getTemperature());
            if (request.getOptions().getMaxTokens() != null)
                chatOptions.setMaxTokens(request.getOptions().getMaxTokens());
            if (request.getOptions().getTopP() != null)
                chatOptions.setTopP(request.getOptions().getTopP());
            if (request.getOptions().getTopK() != null)
                chatOptions.setTopK(request.getOptions().getTopK());
            if (request.getOptions().getPresencePenalty() != null)
                chatOptions.setPresencePenalty(request.getOptions().getPresencePenalty());
            if (request.getOptions().getFrequencyPenalty() != null)
                chatOptions.setFrequencyPenalty(request.getOptions().getFrequencyPenalty());
            spec.options(chatOptions);
            log.debug("Applied ChatOptions instance from ModelOptions");
        }

        // final: stream response (we always stream as Flux<String> — caller can buffer if needed)
        return spec.stream().content();
    }

    /**
     * Dynamically loads tool definitions from registry and maps them to callbacks.
     */
    @SneakyThrows
    private Flux<ToolCallback> getDynamicTools(ChatRequestDto request, User user) {
        log.debug("🔍 Fetching available tools from registry...");

        return getToolHubClient().getStream(user)
                .filter(toolDto -> isToolIncluded(toolDto, request.getEnabledTools()))
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

    /**
     * Resolve TemplateRef (INLINE | BASE64)
     */
    private String resolveTemplate(ChatRequestDto.TemplateRef ref) {
        if (ref == null) return null;
        if (ref.getType() == null) throw new IllegalArgumentException("TemplateRef.type must not be null");
        switch (ref.getType()) {
            case INLINE -> {
                return ref.getContent();
            }
            case BASE64 -> {
                byte[] decoded = Base64.getDecoder().decode(ref.getContent());
                return new String(decoded, StandardCharsets.UTF_8);
            }
            default ->
                    throw new IllegalArgumentException("Only INLINE and BASE64 TemplateRef types are supported. Found: " + ref.getType());
        }
    }

    default Mono<EmbeddingResponseDto> embedding(EmbeddingRequestDto request, User user) {
        log.info("🧩 Starting embedding. model='{}', requestId='{}'",
                request == null ? null : request.getModel(),
                request == null ? null : request.getRequestId());

        return Mono.justOrEmpty(request)
                .switchIfEmpty(Mono.error(new IllegalArgumentException("EmbeddingRequestDto must not be null")))
                .flatMap(this::executeEmbedding)
                .doOnSuccess(res -> log.info("🧩 Embedding completed. model='{}', vectors='{}'",
                        res.getModel(), res.getEmbeddings().size()))
                .doOnError(err -> log.error("❌ Embedding failed. model='{}', requestId='{}', error={}",
                        request.getModel(), request.getRequestId(), err.toString()));
    }


    private Mono<EmbeddingResponseDto> executeEmbedding(EmbeddingRequestDto request) {
        log.debug("⚙️ Building EmbeddingClient for model='{}', requestId='{}'",
                request.getModel(), request.getRequestId());

        EmbeddingOptions options = null;
        if (request.getOptions() != null) {
            options = EmbeddingOptionsBuilder.builder()
                    .withDimensions(request.getOptions().getDimensions())
                    .withModel(request.getOptions().getModel())
                    .build();
        }

        EmbeddingRequest embeddingRequest = new EmbeddingRequest(request.getInputs(), options);
        AbstractEmbeddingModel embeddingModel = getEmbeddingModel(request.getModel());
        EmbeddingResponse embeddingResponse = embeddingModel.call(embeddingRequest);
        return Mono.just(prepareEmbeddingResponse(request, embeddingResponse));
    }

    private EmbeddingResponseDto prepareEmbeddingResponse(EmbeddingRequestDto request, EmbeddingResponse response) {
        return EmbeddingResponseDto.builder()
                .model(request.getModel())
                .requestId(request.getRequestId())
                .embeddings(response.getResults().stream()
                        .map(this::prepareEmbedding)
                        .toList())
                .build();
    }

    private ir.msob.manak.domain.model.ai.embedding.Embedding prepareEmbedding(Embedding result) {
        return ir.msob.manak.domain.model.ai.embedding.Embedding.builder()
                .index(result.getIndex())
                .embedding(result.getOutput())
                .build();
    }


}
