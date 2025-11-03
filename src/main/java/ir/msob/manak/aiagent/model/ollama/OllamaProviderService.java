package ir.msob.manak.aiagent.model.ollama;

import com.fasterxml.jackson.databind.ObjectMapper;
import ir.msob.manak.aiagent.client.RegistryClient;
import ir.msob.manak.aiagent.model.Invoker;
import ir.msob.manak.aiagent.model.ModelProviderService;
import ir.msob.manak.aiagent.model.ToolSchemaUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class OllamaProviderService implements ModelProviderService {

    private final OllamaRegistry ollamaRegistry;
    private final RegistryClient registryClient;
    private final Invoker invoker;
    private final ToolSchemaUtils toolSchemaUtils;
    private final ObjectMapper objectMapper;

    @Override
    public RegistryClient getRegistryClient() {
        return registryClient;
    }

    @Override
    public <CM extends ChatModel> CM getChatModel(String key) {
        return (CM) ollamaRegistry.getModels().get(key);
    }

    @Override
    public Invoker getInvoker() {
        return invoker;
    }

    @Override
    public ToolSchemaUtils getToolSchemaUtils() {
        return toolSchemaUtils;
    }

    @Override
    public ObjectMapper getObjectMapper() {
        return objectMapper;
    }

}