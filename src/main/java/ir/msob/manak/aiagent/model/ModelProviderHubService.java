package ir.msob.manak.aiagent.model;

import ir.msob.jima.core.commons.exception.runtime.CommonRuntimeException;
import ir.msob.manak.aiagent.model.ollama.OllamaProviderService;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class ModelProviderHubService {
    public static final String OLLAMA_TYPE = "Ollama";
    private final OllamaProviderService ollamaProviderService;
    private final Logger log = LoggerFactory.getLogger(ModelProviderHubService.class);

    public ModelProviderService getProvider(String type) {
        if (OLLAMA_TYPE.equals(type)) {
            return ollamaProviderService;
        }
        throw new CommonRuntimeException("Provider not found");
    }
}