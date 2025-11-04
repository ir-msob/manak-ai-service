package ir.msob.manak.aiagent.model;

import ir.msob.jima.core.commons.exception.runtime.CommonRuntimeException;
import ir.msob.manak.aiagent.model.ollama.OllamaProviderService;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

/**
 * Central hub responsible for providing the correct model provider service
 * (e.g., Ollama, OpenAI, etc.) based on model type.
 */
@Service
@RequiredArgsConstructor
public class ModelProviderHubService {

    public static final String OLLAMA_TYPE = "Ollama";
    private static final Logger log = LoggerFactory.getLogger(ModelProviderHubService.class);
    private final OllamaProviderService ollamaProviderService;

    /**
     * Retrieves the provider service implementation for the given model type.
     *
     * @param type the model provider type (e.g., "Ollama")
     * @return the corresponding {@link ModelProviderService}
     * @throws CommonRuntimeException if no matching provider is found
     */
    public ModelProviderService getProvider(String type) {
        log.debug("Resolving model provider for type: {}", type);

        if (OLLAMA_TYPE.equalsIgnoreCase(type)) {
            return ollamaProviderService;
        }
        throw new CommonRuntimeException("Provider not found for type: " + type);
    }
}
