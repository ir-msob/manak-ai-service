package ir.msob.manak.chat.model;

import ir.msob.manak.chat.util.RobustSafeParameterCoercer;
import ir.msob.manak.domain.model.common.model.ParameterDescriptor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Map;
import java.util.Objects;

public record ToolInvocationAdapter(String toolId,
                                    ToolInvoker toolInvoker,
                                    Map<String, ParameterDescriptor> inputSchema,
                                    RobustSafeParameterCoercer coercer) {

    private static final Logger log = LoggerFactory.getLogger(ToolInvocationAdapter.class);

    public ToolInvocationAdapter(String toolId,
                                 ToolInvoker toolInvoker,
                                 Map<String, ParameterDescriptor> inputSchema,
                                 RobustSafeParameterCoercer coercer) {
        this.toolId = Objects.requireNonNull(toolId, "Tool ID must not be null");
        this.toolInvoker = Objects.requireNonNull(toolInvoker, "Invoker must not be null");
        this.inputSchema = inputSchema == null ? Map.of() : inputSchema;
        this.coercer = coercer;
    }

    public Object handle(Map<String, Object> parameters) {
        log.debug("Handling tool execution for toolId: {}, parameters: {}", toolId, parameters);

        Map<String, Object> coercedParams = coercer.coerce(parameters, inputSchema);

        log.debug("Tool parameter coercion completed for toolId: {}, coercedParams: {}", toolId, coercedParams);

        Object result = toolInvoker.invoke(toolId, coercedParams);

        log.debug("Tool execution completed for toolId: {}", toolId);

        return result;
    }
}