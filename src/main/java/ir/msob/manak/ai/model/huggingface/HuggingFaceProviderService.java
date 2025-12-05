package ir.msob.manak.ai.model.huggingface;

import com.fasterxml.jackson.databind.ObjectMapper;
import ir.msob.jima.core.commons.exception.datanotfound.DataNotFoundException;
import ir.msob.manak.ai.model.ModelProviderService;
import ir.msob.manak.ai.util.ToolSchemaUtil;
import ir.msob.manak.domain.model.ai.modelspecification.ModelSpecification;
import ir.msob.manak.domain.service.client.ToolHubClient;
import ir.msob.manak.domain.service.toolhub.ToolInvoker;
import lombok.RequiredArgsConstructor;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.embedding.AbstractEmbeddingModel;
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
        return huggingFaceRegistry.getChatModels()
                .stream()
                .filter(entry -> entry.getKey().equals(key))
                .filter(entry -> entry.getModelTypes().contains(ModelSpecification.ModelType.CHAT))
                .findFirst()
                .map(entry -> (CM) entry.getModel())
                .orElseThrow(() -> new DataNotFoundException(
                        "Model not found for key: " + key));
    }

    @Override
    public <CM extends AbstractEmbeddingModel> CM getEmbeddingModel(String key) {
        return huggingFaceRegistry.getEmbeddingModels()
                .stream()
                .filter(entry -> entry.getKey().equals(key))
                .filter(entry -> entry.getModelTypes().contains(ModelSpecification.ModelType.EMBEDDING))
                .findFirst()
                .map(entry -> (CM) entry.getModel())
                .orElseThrow(() -> new DataNotFoundException(
                        "Model not found for key: " + key));
    }

    public <CM extends ChatModel> CM getSummarizerModel(String key) {
        return huggingFaceRegistry.getSummarizerModels()
                .stream()
                .filter(entry -> entry.getKey().equals(key))
                .filter(entry -> entry.getModelTypes().contains(ModelSpecification.ModelType.SUMMARIZER))
                .findFirst()
                .map(entry -> (CM) entry.getModel())
                .orElseThrow(() -> new DataNotFoundException("Model not found for key: " + key));
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
