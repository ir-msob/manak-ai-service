package ir.msob.manak.ai.model;

import ir.msob.manak.core.model.jima.security.User;
import ir.msob.manak.domain.model.ai.chat.ChatRequestDto;
import ir.msob.manak.domain.model.ai.embedding.EmbeddingRequestDto;
import ir.msob.manak.domain.model.ai.embedding.EmbeddingResponseDto;
import ir.msob.manak.domain.model.ai.summarizer.SummarizerRequestDto;
import ir.msob.manak.domain.model.ai.summarizer.SummarizerResponseDto;
import org.apache.logging.log4j.util.Strings;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.embedding.*;
import org.springframework.ai.template.st.StTemplateRenderer;
import org.springframework.ai.tool.ToolCallback;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.util.List;
import java.util.Objects;

/**
 * Base interface for AI model provider services (e.g., Ollama, OpenAI, etc.)
 * that integrate dynamically registered tools.
 * <p>
 * Adapted to work with the new ChatRequestDto (role-based messages, templates, INLINE/BASE64 content).
 */
public interface ModelProviderService {

    Logger log = LoggerFactory.getLogger(ModelProviderService.class);

    ToolManager getToolManager();

    <CM extends ChatModel> CM getChatModel(String key);

    <CM extends ChatModel> CM getSummarizerModel(String key);

    <CM extends AbstractEmbeddingModel> CM getEmbeddingModel(String key);


    /**
     * Handles a chat request with dynamic tool registration and streaming response.
     */
    default Flux<String> chat(ChatRequestDto request, User user) {
        log.info("💬 Starting chat for model '{}', simpleMessage='{}', requestId='{}'",
                request == null ? "null" : request.getModel(),
                request == null ? null : request.getSimpleMessage(),
                request == null ? null : request.getRequestId());

        Flux<ToolCallback> toolCallbacksFlux = request != null && request.isToolsEnabled() ?
                getToolManager().getDynamicTools(request.getEnabledTools(), user) :
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

        var spec = ChatClient.create(getChatModel(request.getModel()))
                .prompt("")
                .templateRenderer(StTemplateRenderer.builder().build());

        // Using MessageBuilder to handle message building
        new MessageBuilder(request).buildMessage(spec);

        if (!toolCallbacks.isEmpty()) {
            spec.toolCallbacks(toolCallbacks);
        }

        return spec.stream().content();
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
            options = EmbeddingOptions.builder()
                    .dimensions(request.getOptions().getDimensions())
                    .model(request.getModel())
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


    default Mono<SummarizerResponseDto> summarize(SummarizerRequestDto request, User user) {
        Objects.requireNonNull(request, "SummarizerRequestDto must not be null");
        log.debug("⚙️ Building SummarizerClient for model '{}' (requestId='{}')",
                request.getModel(), request.getRequestId());

        var chatClient = ChatClient.create(getSummarizerModel(request.getModel()));

        List<String> summaries = request.getInputs()
                .stream()
                .map(s -> chatClient.prompt(s).call().content())
                .toList();

        String merged = Strings.join(summaries, '\n');

        String finalSummary = chatClient.prompt(merged).call().content();

        return Mono.just(
                SummarizerResponseDto.builder()
                        .requestId(request.getRequestId())
                        .model(request.getModel())
                        .finalSummary(finalSummary)
                        .inputSummaries(summaries)
                        .build()
        );
    }
}
