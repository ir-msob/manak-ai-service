package ir.msob.manak.aiagent.model.ollama;

import io.micrometer.observation.ObservationRegistry;
import ir.msob.jima.core.commons.filter.Filter;
import ir.msob.jima.core.commons.logger.Logger;
import ir.msob.jima.core.commons.logger.LoggerFactory;
import ir.msob.manak.aiagent.modelspecification.ModelSpecificationService;
import ir.msob.manak.core.service.jima.security.UserService;
import ir.msob.manak.domain.model.aiagent.modelspecification.ModelSpecificationCriteria;
import lombok.RequiredArgsConstructor;
import org.springframework.ai.model.tool.DefaultToolCallingManager;
import org.springframework.ai.model.tool.DefaultToolExecutionEligibilityPredicate;
import org.springframework.ai.model.tool.ToolCallingManager;
import org.springframework.ai.ollama.OllamaChatModel;
import org.springframework.ai.ollama.api.OllamaApi;
import org.springframework.ai.ollama.api.OllamaOptions;
import org.springframework.ai.ollama.management.ModelManagementOptions;
import org.springframework.ai.retry.RetryUtils;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.retry.support.RetryTemplate;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import static ir.msob.manak.aiagent.model.ModelProviderHubService.OLLAMA_TYPE;

@Configuration
@RequiredArgsConstructor
public class OllamaConfiguration {
    private static final Logger log = LoggerFactory.getLogger(OllamaConfiguration.class);

    private final Map<String, OllamaChatModel> models = new ConcurrentHashMap<>();


    @Bean
    @Primary
    public Map<String, OllamaChatModel> ollamaChatModels(
            ToolCallingManager toolCallingManager,
            ObservationRegistry observationRegistry,
            ModelManagementOptions modelManagementOptions,
            RetryTemplate retryTemplate,
            ModelSpecificationService modelSpecificationService,
            UserService userService) {

        loadModelsAsync(modelSpecificationService, userService, toolCallingManager,
                observationRegistry, modelManagementOptions, retryTemplate);

        return models;
    }

    private void loadModelsAsync(ModelSpecificationService modelSpecificationService,
                                 UserService userService,
                                 ToolCallingManager toolCallingManager,
                                 ObservationRegistry observationRegistry,
                                 ModelManagementOptions modelManagementOptions,
                                 RetryTemplate retryTemplate) {

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

                        models.put(spec.getKey(), chatModel);

                    } catch (Exception e) {
                        log.error("Error creating model for specification: {}", spec, e);
                    }
                })
                .doOnComplete(() -> log.info("Loaded {} models from database", models.size()))
                .subscribe();
    }

    @Bean
    @ConditionalOnMissingBean
    public ToolCallingManager toolCallingManager() {
        return DefaultToolCallingManager.builder().build();
    }

    @Bean
    @ConditionalOnMissingBean
    public ObservationRegistry observationRegistry() {
        return ObservationRegistry.create();
    }

    @Bean
    @ConditionalOnMissingBean
    public ModelManagementOptions modelManagementOptions() {
        return ModelManagementOptions.builder().build();
    }

    @Bean
    @ConditionalOnMissingBean
    public RetryTemplate retryTemplate() {
        return RetryUtils.DEFAULT_RETRY_TEMPLATE;
    }
}
