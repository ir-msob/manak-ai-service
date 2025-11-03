package ir.msob.manak.aiagent.model.ollama;

import ir.msob.manak.aiagent.client.RegistryClient;
import ir.msob.manak.aiagent.model.Invoker;
import ir.msob.manak.aiagent.model.ModelProviderService;
import lombok.RequiredArgsConstructor;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.ollama.OllamaChatModel;
import org.springframework.stereotype.Service;

import java.util.Map;

@Service
@RequiredArgsConstructor
public class OllamaProviderService implements ModelProviderService {

    private final Map<String, OllamaChatModel> ollamaChatModels;
    private final RegistryClient registryClient;
    private final Invoker invoker;

    @Override
    public RegistryClient getRegistryClient() {
        return registryClient;
    }

    @Override
    public <CM extends ChatModel> CM getChatModel(String key) {
        return (CM) ollamaChatModels.get(key);
    }

    @Override
    public Invoker getInvoker() {
        return null;
    }

}