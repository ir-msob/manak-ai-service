package ir.msob.manak.aiagent.model.ollama;

import io.micrometer.observation.ObservationRegistry;
import ir.msob.jima.core.commons.filter.Filter;
import ir.msob.jima.core.commons.logger.Logger;
import ir.msob.jima.core.commons.logger.LoggerFactory;
import ir.msob.manak.aiagent.modelspecification.ModelSpecificationService;
import ir.msob.manak.core.service.jima.security.UserService;
import ir.msob.manak.domain.model.aiagent.modelspecification.ModelSpecificationCriteria;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import org.springframework.ai.model.tool.DefaultToolExecutionEligibilityPredicate;
import org.springframework.ai.model.tool.ToolCallingManager;
import org.springframework.ai.ollama.OllamaChatModel;
import org.springframework.ai.ollama.api.OllamaApi;
import org.springframework.ai.ollama.api.OllamaOptions;
import org.springframework.ai.ollama.management.ModelManagementOptions;
import org.springframework.retry.support.RetryTemplate;
import org.springframework.stereotype.Component;

import static ir.msob.manak.aiagent.model.ModelProviderHubService.OLLAMA_TYPE;

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
                .type(Filter.eq(OLLAMA_TYPE))
                .build();

        modelSpecificationService.getStream(criteria, userService.getSystemUser())
                .doOnNext(spec -> {
                    try {
                        OllamaApi ollamaApi = OllamaApi.builder()
                                .baseUrl(spec.getBaseUrl())
                                .build();

                        OllamaOptions options = OllamaOptions.builder()
                                .model(spec.getModelName())
                                .temperature(spec.getTemperature())
                                .numPredict(spec.getNumPredict())
                                .build();

                        OllamaChatModel chatModel = new OllamaChatModel(
                                ollamaApi,
                                options,
                                toolCallingManager,
                                observationRegistry,
                                modelManagementOptions,
                                new DefaultToolExecutionEligibilityPredicate(),
                                retryTemplate
                        );

                        ollamaRegistry.getModels().put(spec.getKey(), chatModel);

                    } catch (Exception e) {
                        log.error("Error creating model for specification: {}", spec, e);
                    }
                })
                .doOnComplete(() -> log.info("Loaded {} models from database", ollamaRegistry.getModels().size()))
                .subscribe();

    }
}
