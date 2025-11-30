package ir.msob.manak.ai.model.huggingface;

import ir.msob.manak.ai.model.ModelEntry;
import lombok.Getter;
import org.springframework.ai.embedding.AbstractEmbeddingModel;
import org.springframework.ai.huggingface.HuggingfaceChatModel;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class HuggingFaceRegistry {
    @Getter
    private final List<ModelEntry<HuggingfaceChatModel>> chatModels = new ArrayList<>();

    @Getter
    private final List<ModelEntry<AbstractEmbeddingModel>> embeddingModels = new ArrayList<>();
}