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
import org.springframework.ai.tool.method.MethodToolCallback;
import reactor.core.publisher.Flux;

import java.lang.reflect.Method;
import java.util.Map;

public interface ModelProviderService {

    RegistryClient getRegistryClient();

    <CM extends ChatModel> CM getChatModel(String key);

    Invoker getInvoker();

    ToolSchemaUtils getToolSchemaUtils();

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

    @SneakyThrows
    private ToolCallback prepareToolCallback(ToolDto toolDto) {
        // build an informative description that includes response schema summary so the LLM can see it
        String description = toolDto.getDescription() == null ? "" : toolDto.getDescription();
        if (toolDto.getOutputSchema() != null) {
            // small, human-readable note; avoid super long raw JSON here — but you can include a concise JSON example
            description += "\n\nResponse format (JSON): " + getToolSchemaUtils().exampleForSchema(toolDto.getOutputSchema());
        }

        ToolDefinition toolDefinition = DefaultToolDefinition.builder()
                .name(toolDto.getToolId())
                .description(description)
                .inputSchema(getToolSchemaUtils().toJsonSchema(toolDto.getInputSchema()))
                .build();

        // prepare metadata with output/error schema strings (for server-side validation)
        ExtendedToolMetadata metadata = ExtendedToolMetadata.builder()
                .outputSchemaJson(getToolSchemaUtils().toJsonSchema(toolDto.getOutputSchema()))
                .errorSchemaJson(getToolSchemaUtils().toJsonSchema(toolDto.getErrorSchema()))
                .version(toolDto.getVersion())
                .build();

        ToolHandler toolHandler = new ToolHandler(toolDto.getToolId(), getInvoker());

        Method handlerMethod = ToolHandler.class.getMethod("handle", Map.class);

        return MethodToolCallback.builder()
                .toolDefinition(toolDefinition)
                .toolMetadata(metadata)
                .toolMethod(handlerMethod)
                .toolObject(toolHandler)
                .build();
    }

}
