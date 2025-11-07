package ir.msob.manak.chat.model;

import ir.msob.manak.chat.util.RobustSafeParameterCoercer;
import ir.msob.manak.domain.model.toolhub.toolprovider.tooldescriptor.ToolParameter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Map;
import java.util.Objects;

/**
 * <p>
 * Acts as a bridge between the AI model’s tool callback and the actual execution logic.
 * It ensures all input parameters are type-safe and schema-compliant before invoking the tool.
 * </p>
 *
 * <p>
 * This adapter:
 * <ul>
 *     <li>Receives raw parameters (possibly untyped or inconsistent types) from model responses.</li>
 *     <li>Uses {@link RobustSafeParameterCoercer} to convert them based on the tool’s {@link ToolParameter} schema.</li>
 *     <li>Delegates the actual execution to the provided {@link ToolInvoker} implementation.</li>
 * </ul>
 * </p>
 *
 * <p>
 * It never throws type conversion exceptions — all coercion is performed in a fault-tolerant way.
 * Any failed conversions are logged at <code>DEBUG</code> level, and the original value is preserved.
 * </p>
 */
public record ToolInvocationAdapter(String toolId,
                                    ToolInvoker toolInvoker,
                                    Map<String, ToolParameter> inputSchema,
                                    RobustSafeParameterCoercer coercer) {

    private static final Logger log = LoggerFactory.getLogger(ToolInvocationAdapter.class);

    /**
     * Constructs a new {@link ToolInvocationAdapter} instance.
     *
     * @param toolId      the unique identifier for the tool; must not be {@code null}
     * @param toolInvoker the functional component responsible for executing the tool logic; must not be {@code null}
     * @param inputSchema the schema describing expected parameter names and types (may be empty but never {@code null})
     * @param coercer     the safe parameter coercer that performs schema-based type conversion
     * @throws NullPointerException if {@code toolId} or {@code toolInvoker} is {@code null}
     */
    public ToolInvocationAdapter(String toolId,
                                 ToolInvoker toolInvoker,
                                 Map<String, ToolParameter> inputSchema,
                                 RobustSafeParameterCoercer coercer) {
        this.toolId = Objects.requireNonNull(toolId, "Tool ID must not be null");
        this.toolInvoker = Objects.requireNonNull(toolInvoker, "Invoker must not be null");
        this.inputSchema = inputSchema == null ? Map.of() : inputSchema;
        this.coercer = coercer;
    }

    /**
     * <p>
     * Executes the tool with the given parameters.
     * </p>
     *
     * <p>
     * Steps performed by this method:
     * <ol>
     *     <li>Logs the received raw parameters for debugging purposes.</li>
     *     <li>Coerces (converts) parameters to match the expected types defined in {@link #inputSchema}
     *     using {@link RobustSafeParameterCoercer#coerce(Map, Map)}.</li>
     *     <li>Invokes the actual tool logic via {@link ToolInvoker#invoke(String, Map)}.</li>
     *     <li>Returns the tool execution result as an arbitrary object.</li>
     * </ol>
     * </p>
     *
     * <p>
     * This method never throws exceptions due to type mismatches; all conversions are best-effort.
     * </p>
     *
     * @param parameters raw input parameters (may contain untyped values from model output)
     * @return the result of executing the tool logic
     */
    public Object handle(Map<String, Object> parameters) {
        log.debug("Handling tool execution for toolId: {}, parameters: {}", toolId, parameters);

        Map<String, Object> coercedParams = coercer.coerce(parameters, inputSchema);

        log.debug("Tool parameter coercion completed for toolId: {}, coercedParams: {}", toolId, coercedParams);

        Object result = toolInvoker.invoke(toolId, coercedParams);

        log.debug("Tool execution completed for toolId: {}", toolId);

        return result;
    }
}
