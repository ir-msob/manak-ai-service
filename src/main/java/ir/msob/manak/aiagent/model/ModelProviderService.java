package ir.msob.manak.aiagent.model;

import ir.msob.manak.aiagent.client.RegistryClient;
import ir.msob.manak.core.model.jima.security.User;
import ir.msob.manak.domain.model.aiagent.chat.ChatRequest;
import ir.msob.manak.domain.model.toolhub.dto.ToolDto;
import lombok.SneakyThrows;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.tool.ToolCallback;
import org.springframework.ai.tool.definition.DefaultToolDefinition;
import org.springframework.ai.tool.definition.ToolDefinition;
import org.springframework.ai.tool.metadata.ToolMetadata;
import org.springframework.ai.tool.method.MethodToolCallback;
import reactor.core.publisher.Flux;

import java.lang.reflect.Method;
import java.util.Map;

public interface ModelProviderService {

    RegistryClient getRegistryClient();

    <CM extends ChatModel> CM getChatModel(String key);

    Invoker getInvoker();

    default Flux<String> chat(ChatRequest dto, User user) {
        return getDynamicTools(dto, user)
                .collectList()
                .flatMapMany(toolCallbacks -> ChatClient.create(getChatModel(dto.getModelSpecificationKey()))
                        .prompt(dto.getMessage())
                        .toolCallbacks(toolCallbacks)
                        .stream()
                        .content());
    }

    @SneakyThrows
    private Flux<ToolCallback> getDynamicTools(ChatRequest dto, User user) {
        return getRegistryClient().getStream(user)
                .filter(toolDto -> dto.getTools().isEmpty() || dto.getTools().contains(toolDto.getToolId()))
                .map(this::prepareToolCallback);
    }

    private ToolCallback prepareToolCallback(ToolDto toolDto) throws NoSuchMethodException {
        ToolDefinition toolDefinition = DefaultToolDefinition.builder()
                .name(toolDto.getToolId())
                .description(toolDto.getDescription()) // ADD output and error schema
                .inputSchema(toolDto.getInputSchema().toString()) // TODO
                .build();

        ToolHandler toolHandler = new ToolHandler(toolDto.getToolId(), getInvoker());

        Method handlerMethod = ToolHandler.class.getMethod("handle", Map.class);

        return MethodToolCallback.builder()
                .toolDefinition(toolDefinition)
                .toolMetadata(ToolMetadata.builder().build())
                .toolMethod(handlerMethod)
                .toolObject(toolHandler)
                .build();
    }
}
