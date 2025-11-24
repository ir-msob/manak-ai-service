package ir.msob.manak.chat.model.huggingface;

import com.fasterxml.jackson.databind.ObjectMapper;
import ir.msob.manak.chat.model.ModelProviderService;
import ir.msob.manak.chat.util.ToolSchemaUtil;
import ir.msob.manak.domain.service.client.ToolHubClient;
import ir.msob.manak.domain.service.toolhub.ToolInvoker;
import lombok.RequiredArgsConstructor;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class HuggingFaceProviderService implements ModelProviderService {

    private final HuggingFaceRegistry huggingFaceRegistry;
    private final ToolHubClient toolHubClient;
    private final ToolInvoker toolInvoker;
    private final ToolSchemaUtil toolSchemaUtil;
    private final ObjectMapper objectMapper;

    @Override
    public ToolHubClient getToolHubClient() {
        return toolHubClient;
    }

    @Override
    public <CM extends ChatModel> CM getChatModel(String key) {
        return (CM) huggingFaceRegistry.getModels().get(key);
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
