package ir.msob.manak.aiagent.model;

import java.io.Serializable;
import java.util.Map;
import java.util.Objects;

public class ToolHandler {
    private final String toolId;
    private final Invoker invoker;

    public ToolHandler(String toolId, Invoker invoker) {
        this.toolId = Objects.requireNonNull(toolId);
        this.invoker = Objects.requireNonNull(invoker);
    }

    /**
     * This is the single method that MethodToolCallback will call.
     * It simply forwards to myTool.invoke(action, params).
     */
    public Object handle(Map<String, Serializable> params) {
        return invoker.invoke(toolId, params);
    }
}
