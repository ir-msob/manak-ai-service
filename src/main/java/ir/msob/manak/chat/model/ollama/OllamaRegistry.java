package ir.msob.manak.chat.model.ollama;

import ir.msob.manak.chat.model.ModelEntry;
import lombok.Getter;
import org.springframework.ai.ollama.OllamaChatModel;
import org.springframework.ai.ollama.OllamaEmbeddingModel;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class OllamaRegistry {
    @Getter
    private final List<ModelEntry<OllamaChatModel>> chatModels = new ArrayList<>();

    @Getter
    private final List<ModelEntry<OllamaEmbeddingModel>> embeddingModels = new ArrayList<>();
}
