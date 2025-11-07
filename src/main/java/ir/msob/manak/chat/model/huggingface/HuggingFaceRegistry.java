package ir.msob.manak.chat.model.huggingface;

import lombok.Getter;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class HuggingFaceRegistry {
    @Getter
    private final Map<String, ChatModel> models = new ConcurrentHashMap<>();
}
