package ir.msob.manak.aiagent.model;

import com.fasterxml.jackson.databind.ObjectMapper;
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
import reactor.core.publisher.Flux;

import java.util.List;

public interface ModelProviderService {

    RegistryClient getRegistryClient();

    <CM extends ChatModel> CM getChatModel(String key);

    Invoker getInvoker();

    ToolSchemaUtils getToolSchemaUtils();

    ObjectMapper getObjectMapper();

    default Flux<String> chat(ChatRequest request, User user) {
        return getDynamicTools(request, user)
                .collectList()
                .flatMapMany(toolCallbacks -> buildChatClient(request, toolCallbacks));
    }

    private Flux<String> buildChatClient(ChatRequest request, List<ToolCallback> toolCallbacks) {
        return ChatClient.create(getChatModel(request.getModelSpecificationKey()))
                .prompt(request.getMessage())
                .toolCallbacks(toolCallbacks)
                .stream()
                .content();
    }

    @SneakyThrows
    private Flux<ToolCallback> getDynamicTools(ChatRequest request, User user) {
        return getRegistryClient().getStream(user)
                .filter(toolDto -> isToolIncluded(toolDto, request.getTools()))
                .map(this::prepareToolCallback);
    }

    private boolean isToolIncluded(ToolDto toolDto, java.util.List<String> requestedTools) {
        return requestedTools.isEmpty() || requestedTools.contains(toolDto.getToolId());
    }

    @SneakyThrows
    private ToolCallback prepareToolCallback(ToolDto toolDto) {
        ToolDefinition toolDefinition = createToolDefinition(toolDto);
        ExtendedToolMetadata metadata = createToolMetadata(toolDto);
        ToolHandler toolHandler = createToolHandler(toolDto);

        return new AdaptiveToolCallback(toolDefinition, metadata, toolHandler, getObjectMapper());
    }

    private ToolDefinition createToolDefinition(ToolDto toolDto) {
        String description = buildToolDescription(toolDto);

        return DefaultToolDefinition.builder()
                .name(toolDto.getToolId())
                .description(description)
                .inputSchema(getToolSchemaUtils().toJsonSchema(toolDto.getInputSchema()))
                .build();
    }

    private String buildToolDescription(ToolDto toolDto) {
        StringBuilder description = new StringBuilder();

        if (toolDto.getDescription() != null) {
            description.append(toolDto.getDescription());
        }

        if (toolDto.getOutputSchema() != null) {
            description.append("\n\nResponse format (JSON): ")
                    .append(getToolSchemaUtils().exampleForSchema(toolDto.getOutputSchema()));
        }

        return description.toString();
    }

    private ExtendedToolMetadata createToolMetadata(ToolDto toolDto) {
        return ExtendedToolMetadata.builder()
                .outputSchemaJson(getToolSchemaUtils().toJsonSchema(toolDto.getOutputSchema()))
                .errorSchemaJson(getToolSchemaUtils().toJsonSchema(toolDto.getErrorSchema()))
                .version(toolDto.getVersion())
                .build();
    }

    private ToolHandler createToolHandler(ToolDto toolDto) {
        return new ToolHandler(toolDto.getToolId(), getInvoker());
    }
}