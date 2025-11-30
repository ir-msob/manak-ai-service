package ir.msob.manak.chat.model.huggingface;

import ir.msob.manak.chat.model.ModelEntry;
import lombok.Getter;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.embedding.AbstractEmbeddingModel;
import org.springframework.ai.huggingface.HuggingfaceChatModel;
import org.springframework.ai.ollama.OllamaChatModel;
import org.springframework.ai.ollama.OllamaEmbeddingModel;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class HuggingFaceRegistry {
    @Getter
    private final List<ModelEntry<HuggingfaceChatModel>> chatModels = new ArrayList<>();

    @Getter
    private final List<ModelEntry<AbstractEmbeddingModel>> embeddingModels = new ArrayList<>();
}