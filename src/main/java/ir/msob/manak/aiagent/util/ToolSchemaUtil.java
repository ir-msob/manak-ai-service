package ir.msob.manak.aiagent.util;

import com.fasterxml.jackson.databind.ObjectMapper;
import ir.msob.manak.domain.model.toolhub.toolprovider.tooldescriptor.ToolParameter;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.util.*;

/**
 * Utility (Spring bean) to convert ToolParameter structures into JSON Schema (and small examples).
 * <p>
 * Uses a single injected ObjectMapper. For pretty output it uses
 * objectMapper.writerWithDefaultPrettyPrinter(), for compact output it uses objectMapper directly.
 */
@Component
@RequiredArgsConstructor
public class ToolSchemaUtil {

    private final ObjectMapper objectMapper;


    /**
     * Convert a map of named parameters to a JSON Schema string (pretty printed).
     */
    public String toJsonSchema(Map<String, ToolParameter> inputSchema) {
        Map<String, Object> root = toJsonSchemaMap(inputSchema);
        try {
            // pretty-print using writerWithDefaultPrettyPrinter()
            return objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(root);
        } catch (Exception ex) {
            throw new RuntimeException("Failed to serialize input schema to JSON", ex);
        }
    }

    /**
     * Produce the JSON Schema as a Map (useful if you want to pass it directly without serializing).
     */
    public Map<String, Object> toJsonSchemaMap(Map<String, ToolParameter> inputSchema) {
        Map<String, Object> root = new LinkedHashMap<>();
        root.put("type", "object");

        Map<String, Object> properties = new LinkedHashMap<>();
        List<String> required = new ArrayList<>();

        if (inputSchema != null) {
            for (Map.Entry<String, ToolParameter> e : inputSchema.entrySet()) {
                String name = e.getKey();
                ToolParameter param = e.getValue();
                properties.put(name, buildParameterSchemaMap(param));
                if (isRequired(param)) {
                    required.add(name);
                }
            }
        }

        root.put("properties", properties);
        if (!required.isEmpty()) {
            root.put("required", required);
        }
        root.put("additionalProperties", false);
        return root;
    }

    /**
     * Convert a single ToolParameter (root) to a JSON Schema string.
     */
    public String toJsonSchema(ToolParameter rootParam) {
        Map<String, Object> schema = buildParameterSchemaMap(rootParam);
        try {
            return objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(schema);
        } catch (Exception ex) {
            throw new RuntimeException("Failed to serialize parameter schema to JSON", ex);
        }
    }

    /**
     * Build a compact (single-line) JSON example for a parameter map (input).
     */
    public String exampleForSchema(Map<String, ToolParameter> schema) {
        Map<String, Object> example = new LinkedHashMap<>();
        if (schema != null) {
            for (Map.Entry<String, ToolParameter> e : schema.entrySet()) {
                example.put(e.getKey(), buildExampleValue(e.getValue()));
            }
        }
        try {
            return objectMapper.writeValueAsString(example); // compact
        } catch (Exception ex) {
            throw new RuntimeException("Failed to serialize example for schema", ex);
        }
    }

    /**
     * Build a compact (single-line) JSON example for a single ToolParameter (output/error).
     */
    public String exampleForSchema(ToolParameter toolParameter) {
        Object example = buildExampleValue(toolParameter);
        try {
            return objectMapper.writeValueAsString(example); // compact
        } catch (Exception ex) {
            throw new RuntimeException("Failed to serialize example for root param", ex);
        }
    }

    // ------------ helper methods (unchanged) ------------

    private Map<String, Object> buildParameterSchemaMap(ToolParameter toolParameter) {
        Map<String, Object> schema = new LinkedHashMap<>();
        if (toolParameter == null) {
            schema.put("type", "string");
            return schema;
        }

        String jsonType = detectJsonType(toolParameter);

        if ("object".equals(jsonType)) {
            schema.put("type", "object");
            Map<String, Object> nestedProps = new LinkedHashMap<>();
            List<String> nestedRequired = new ArrayList<>();
            Map<String, ToolParameter> props = safeGetProperties(toolParameter);
            if (props != null && !props.isEmpty()) {
                for (Map.Entry<String, ToolParameter> sub : props.entrySet()) {
                    nestedProps.put(sub.getKey(), buildParameterSchemaMap(sub.getValue()));
                    if (isRequired(sub.getValue())) {
                        nestedRequired.add(sub.getKey());
                    }
                }
            }
            schema.put("properties", nestedProps);
            if (!nestedRequired.isEmpty()) schema.put("required", nestedRequired);
            schema.put("additionalProperties", false);
        } else if ("array".equals(jsonType)) {
            schema.put("type", "array");
            ToolParameter items = safeGetItems(toolParameter);
            if (items != null) schema.put("items", buildParameterSchemaMap(items));
            else schema.put("items", Collections.singletonMap("type", "string"));
        } else {
            schema.put("type", jsonType);
        }

        if (toolParameter.getDescription() != null) schema.put("description", toolParameter.getDescription());
        if (toolParameter.getExample() != null) schema.put("example", buildExampleValue(toolParameter));
        if (toolParameter.getDefaultValue() != null) schema.put("default", toolParameter.getDefaultValue());

        if (toolParameter.getEnumValues() != null && !toolParameter.getEnumValues().isEmpty()) {
            schema.put("enum", toolParameter.getEnumValues());
        }
        if (toolParameter.getMinimum() != null) schema.put("minimum", toolParameter.getMinimum());
        if (toolParameter.getMaximum() != null) schema.put("maximum", toolParameter.getMaximum());
        if (toolParameter.getMinLength() != null) schema.put("minLength", toolParameter.getMinLength());
        if (toolParameter.getMaxLength() != null) schema.put("maxLength", toolParameter.getMaxLength());
        if (toolParameter.getPattern() != null) schema.put("pattern", toolParameter.getPattern());

        if (Boolean.TRUE.equals(toolParameter.getNullable())) {
            schema.compute("type", (k, t) -> Arrays.asList(t, "null"));
        }

        return schema;
    }

    private Object buildExampleValue(ToolParameter param) {
        if (param == null) return null;

        Object example = param.getExample();
        if (example != null) return example;

        Object def = param.getDefaultValue();
        if (def != null) return List.of(def);

        return null;
    }

    private String detectJsonType(ToolParameter param) {
        if (param == null || param.getType() == null) return "string";
        return switch (param.getType()) {
            case STRING -> "string";
            case NUMBER -> "number";
            case BOOLEAN -> "boolean";
            case OBJECT -> "object";
            case ARRAY -> "array";
        };
    }

    private boolean isRequired(ToolParameter param) {
        if (param == null) return false;
        try {
            return param.isRequired();
        } catch (Exception e) {
            return false;
        }
    }

    private Map<String, ToolParameter> safeGetProperties(ToolParameter param) {
        try {
            return param.getProperties();
        } catch (Exception e) {
            return null;
        }
    }

    private ToolParameter safeGetItems(ToolParameter param) {
        try {
            return param.getItems();
        } catch (Exception e) {
            return null;
        }
    }
}
