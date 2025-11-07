package ir.msob.manak.chat.model.ollama;

import lombok.Getter;
import org.springframework.ai.ollama.OllamaChatModel;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class OllamaRegistry {
    @Getter
    private final Map<String, OllamaChatModel> models = new ConcurrentHashMap<>();
}
