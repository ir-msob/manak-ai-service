package ir.msob.manak.aiagent.model;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.Serializable;
import java.util.Map;
import java.util.Objects;

/**
 * Handles tool execution by delegating to an invoker.
 * This class serves as a bridge between tool callbacks and actual tool execution.
 */
public record ToolHandler(String toolId, Invoker invoker) {

    private static final Logger log = LoggerFactory.getLogger(ToolHandler.class);

    /**
     * Constructs a new ToolHandler with the specified tool ID and invoker.
     *
     * @param toolId  the unique identifier for the tool, must not be null
     * @param invoker the invoker that will execute the tool, must not be null
     * @throws NullPointerException if toolId or invoker is null
     */
    public ToolHandler(String toolId, Invoker invoker) {
        this.toolId = Objects.requireNonNull(toolId, "Tool ID must not be null");
        this.invoker = Objects.requireNonNull(invoker, "Invoker must not be null");
    }

    /**
     * Handles tool execution by delegating to the invoker.
     * This method is called by MethodToolCallback to execute the tool.
     *
     * @param parameters the parameters for tool execution
     * @return the result of tool execution
     */
    public Serializable handle(Map<String, Serializable> parameters) {
        log.debug("Handling tool execution for toolId: {}, parameters: {}", toolId, parameters);

        Serializable result = invoker.invoke(toolId, parameters);

        log.debug("Tool execution completed for toolId: {}", toolId);

        return result;
    }
}