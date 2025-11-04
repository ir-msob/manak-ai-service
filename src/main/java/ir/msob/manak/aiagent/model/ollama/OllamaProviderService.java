package ir.msob.manak.aiagent.model.ollama;

import com.fasterxml.jackson.databind.ObjectMapper;
import ir.msob.manak.aiagent.client.RegistryClient;
import ir.msob.manak.aiagent.model.ModelProviderService;
import ir.msob.manak.aiagent.model.ToolInvoker;
import ir.msob.manak.aiagent.util.ToolSchemaUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class OllamaProviderService implements ModelProviderService {

    private final OllamaRegistry ollamaRegistry;
    private final RegistryClient registryClient;
    private final ToolInvoker toolInvoker;
    private final ToolSchemaUtil toolSchemaUtil;
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
    public ToolInvoker getToolInvoker() {
        return toolInvoker;
    }

    @Override
    public ToolSchemaUtil getToolSchemaUtil() {
        return toolSchemaUtil;
    }

    @Override
    public ObjectMapper getObjectMapper() {
        return objectMapper;
    }

}