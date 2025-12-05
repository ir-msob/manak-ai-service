package ir.msob.manak.ai.model.ollama;

import io.micrometer.observation.ObservationRegistry;
import ir.msob.jima.core.commons.filter.Filter;
import ir.msob.jima.core.commons.logger.Logger;
import ir.msob.jima.core.commons.logger.LoggerFactory;
import ir.msob.manak.ai.model.ModelEntry;
import ir.msob.manak.ai.modelspecification.ModelSpecificationService;
import ir.msob.manak.core.service.jima.security.UserService;
import ir.msob.manak.domain.model.ai.modelspecification.ModelSpecification;
import ir.msob.manak.domain.model.ai.modelspecification.ModelSpecificationCriteria;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import org.springframework.ai.model.tool.DefaultToolExecutionEligibilityPredicate;
import org.springframework.ai.model.tool.ToolCallingManager;
import org.springframework.ai.ollama.OllamaChatModel;
import org.springframework.ai.ollama.OllamaEmbeddingModel;
import org.springframework.ai.ollama.api.OllamaApi;
import org.springframework.ai.ollama.api.OllamaChatOptions;
import org.springframework.ai.ollama.api.OllamaEmbeddingOptions;
import org.springframework.ai.ollama.management.ModelManagementOptions;
import org.springframework.retry.support.RetryTemplate;
import org.springframework.stereotype.Component;

import static ir.msob.manak.ai.model.ModelProviderHubService.OLLAMA_TYPE;

@Component
@RequiredArgsConstructor
public class OllamaStartup {

    private static final Logger log = LoggerFactory.getLogger(OllamaStartup.class);

    private final OllamaRegistry ollamaRegistry;
    private final ToolCallingManager toolCallingManager;
    private final ObservationRegistry observationRegistry;
    private final ModelManagementOptions modelManagementOptions;
    private final RetryTemplate retryTemplate;
    private final ModelSpecificationService modelSpecificationService;
    private final UserService userService;

    @PostConstruct
    public void startup() {
        ModelSpecificationCriteria criteria = ModelSpecificationCriteria.builder()
                .providerType(Filter.eq(OLLAMA_TYPE))
                .build();

        modelSpecificationService.getStream(criteria, userService.getSystemUser())
                .doOnNext(this::createModelFromSpec)
                .doOnComplete(this::logSummary)
                .subscribe();
    }

    /**
     * ─────────────────────────────────────────────────────────────
     * Create model instance (chat or embedding) from spec
     * ─────────────────────────────────────────────────────────────
     */
    private void createModelFromSpec(ModelSpecification spec) {
        try {
            OllamaApi api = createApi(spec.getBaseUrl());

            if (spec.getModelTypes().contains(ModelSpecification.ModelType.CHAT)) {
                registerChatModel(spec, api);
            }

            if (spec.getModelTypes().contains(ModelSpecification.ModelType.EMBEDDING)) {
                registerEmbeddingModel(spec, api);
            }

            if (spec.getModelTypes().contains(ModelSpecification.ModelType.SUMMARIZER)) {
                registerSummarizerModel(spec, api);
            }


        } catch (Exception e) {
            log.error("❌ Failed to create Ollama model for spec: {}", spec.getKey(), e);
        }
    }

    /**
     * ─────────────────────────────────────────────────────────────
     * Create API client
     * ─────────────────────────────────────────────────────────────
     */
    private OllamaApi createApi(String baseUrl) {
        return OllamaApi.builder().baseUrl(baseUrl).build();
    }

    /**
     * ─────────────────────────────────────────────────────────────
     * Register Chat Model
     * ─────────────────────────────────────────────────────────────
     */
    private void registerChatModel(ModelSpecification spec, OllamaApi api) {

        OllamaChatOptions options = OllamaChatOptions.builder()
                .model(spec.getModelName())
                .temperature(spec.getTemperature())
                .numPredict(spec.getNumPredict())
                .build();

        OllamaChatModel chatModel = new OllamaChatModel(
                api,
                options,
                toolCallingManager,
                observationRegistry,
                modelManagementOptions,
                new DefaultToolExecutionEligibilityPredicate(),
                retryTemplate
        );

        ollamaRegistry.getChatModels().add(
                ModelEntry.<OllamaChatModel>builder()
                        .key(spec.getKey())
                        .modelTypes(spec.getModelTypes())
                        .model(chatModel)
                        .build()
        );

        log.info("✔️ Registered CHAT model: {}", spec.getKey());
    }

    /**
     * ─────────────────────────────────────────────────────────────
     * Register Embedding Model
     * ─────────────────────────────────────────────────────────────
     */
    private void registerEmbeddingModel(ModelSpecification spec, OllamaApi api) {

        OllamaEmbeddingOptions options = OllamaEmbeddingOptions.builder()
                .model(spec.getModelName())
                .build();

        OllamaEmbeddingModel embeddingModel = new OllamaEmbeddingModel(
                api,
                options,
                observationRegistry,
                modelManagementOptions
        );

        ollamaRegistry.getEmbeddingModels().add(
                ModelEntry.<OllamaEmbeddingModel>builder()
                        .key(spec.getKey())
                        .modelTypes(spec.getModelTypes())
                        .model(embeddingModel)
                        .build()
        );

        log.info("✔️ Registered EMBEDDING model: {}", spec.getKey());
    }

    /**
     * ─────────────────────────────────────────────────────────────
     * Register Summarizer Model
     * ─────────────────────────────────────────────────────────────
     */
    private void registerSummarizerModel(ModelSpecification spec, OllamaApi api) {

        OllamaChatOptions options = OllamaChatOptions.builder()
                .model(spec.getModelName())
                .temperature(spec.getTemperature())
                .numPredict(spec.getNumPredict())
                .build();

        OllamaChatModel chatModel = new OllamaChatModel(
                api,
                options,
                toolCallingManager,
                observationRegistry,
                modelManagementOptions,
                new DefaultToolExecutionEligibilityPredicate(),
                retryTemplate
        );

        ollamaRegistry.getSummarizerModels().add(
                ModelEntry.<OllamaChatModel>builder()
                        .key(spec.getKey())
                        .modelTypes(spec.getModelTypes())
                        .model(chatModel)
                        .build()
        );

        log.info("✔️ Registered Summarizer model: {}", spec.getKey());
    }


    /**
     * ─────────────────────────────────────────────────────────────
     * Log summary after loading all models
     * ─────────────────────────────────────────────────────────────
     */
    private void logSummary() {
        log.info(
                "✅ Loaded Ollama models: {} chat, {} embedding",
                ollamaRegistry.getChatModels().size(),
                ollamaRegistry.getEmbeddingModels().size()
        );
    }
}
