package ir.msob.manak.chat.util;

import com.fasterxml.jackson.databind.ObjectMapper;
import ir.msob.manak.domain.model.toolhub.toolprovider.tooldescriptor.ParameterDescriptor;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.util.*;

/**
 * Utility (Spring bean) to convert ParameterDescriptor structures into JSON Schema (and small examples).
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
    public String toJsonSchema(Map<String, ParameterDescriptor> inputSchema) {
        Map<String, Object> root = toJsonSchemaMap(inputSchema);
        try {
            return objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(root);
        } catch (Exception ex) {
            throw new RuntimeException("Failed to serialize input schema to JSON", ex);
        }
    }

    /**
     * Produce the JSON Schema as a Map (useful if you want to pass it directly without serializing).
     */
    public Map<String, Object> toJsonSchemaMap(Map<String, ParameterDescriptor> inputSchema) {
        Map<String, Object> root = new LinkedHashMap<>();
        root.put("type", "object");

        Map<String, Object> properties = new LinkedHashMap<>();
        List<String> required = new ArrayList<>();

        if (inputSchema != null) {
            for (Map.Entry<String, ParameterDescriptor> e : inputSchema.entrySet()) {
                String name = e.getKey();
                ParameterDescriptor param = e.getValue();
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
     * Convert a single ParameterDescriptor (root) to a JSON Schema string.
     */
    public String toJsonSchema(ParameterDescriptor rootParam) {
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
    public String exampleForSchema(Map<String, ParameterDescriptor> schema) {
        Map<String, Object> example = new LinkedHashMap<>();
        if (schema != null) {
            for (Map.Entry<String, ParameterDescriptor> e : schema.entrySet()) {
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
     * Build a compact (single-line) JSON example for a single ParameterDescriptor (output/error).
     */
    public String exampleForSchema(ParameterDescriptor param) {
        Object example = buildExampleValue(param);
        try {
            return objectMapper.writeValueAsString(example); // compact
        } catch (Exception ex) {
            throw new RuntimeException("Failed to serialize example for root param", ex);
        }
    }

    // ------------ helper methods (adapted) ------------

    private Map<String, Object> buildParameterSchemaMap(ParameterDescriptor param) {
        Map<String, Object> schema = new LinkedHashMap<>();
        if (param == null) {
            schema.put("type", "string");
            return schema;
        }

        String jsonType = detectJsonType(param);

        if ("object".equals(jsonType)) {
            schema.put("type", "object");
            Map<String, Object> nestedProps = new LinkedHashMap<>();
            List<String> nestedRequired = new ArrayList<>();
            Map<String, ParameterDescriptor> props = safeGetProperties(param);
            if (props != null && !props.isEmpty()) {
                for (Map.Entry<String, ParameterDescriptor> sub : props.entrySet()) {
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
            ParameterDescriptor items = safeGetItems(param);
            if (items != null) schema.put("items", buildParameterSchemaMap(items));
            else schema.put("items", Collections.singletonMap("type", "string"));
        } else {
            schema.put("type", jsonType);
        }

        if (param.getDescription() != null) schema.put("description", param.getDescription());
        if (param.getDefaultValue() != null) schema.put("default", param.getDefaultValue());
        if (param.getExamples() != null && !param.getExamples().isEmpty()) schema.put("examples", param.getExamples());

        if (param.getEnumValues() != null && !param.getEnumValues().isEmpty()) {
            schema.put("enum", param.getEnumValues());
        }
        if (param.getMinimum() != null) schema.put("minimum", param.getMinimum());
        if (param.getMaximum() != null) schema.put("maximum", param.getMaximum());
        if (param.getMinLength() != null) schema.put("minLength", param.getMinLength());
        if (param.getMaxLength() != null) schema.put("maxLength", param.getMaxLength());
        if (param.getPattern() != null) schema.put("pattern", param.getPattern());

        if (Boolean.TRUE.equals(param.getNullable())) {
            schema.compute("type", (k, t) -> Arrays.asList(t, "null"));
        }

        return schema;
    }

    private Object buildExampleValue(ParameterDescriptor param) {
        if (param == null) return null;

        if (param.getExamples() != null && !param.getExamples().isEmpty()) return param.getExamples().getFirst();

        if (param.getDefaultValue() != null) return param.getDefaultValue();

        return null;
    }

    private String detectJsonType(ParameterDescriptor param) {
        if (param == null || param.getType() == null) return "string";
        return switch (param.getType()) {
            case STRING -> "string";
            case NUMBER -> "number";
            case BOOLEAN -> "boolean";
            case OBJECT -> "object";
            case ARRAY -> "array";
        };
    }

    private boolean isRequired(ParameterDescriptor param) {
        if (param == null) return false;
        try {
            return param.isRequired();
        } catch (Exception e) {
            return false;
        }
    }

    private Map<String, ParameterDescriptor> safeGetProperties(ParameterDescriptor param) {
        try {
            return param.getProperties();
        } catch (Exception e) {
            return null;
        }
    }

    private ParameterDescriptor safeGetItems(ParameterDescriptor param) {
        try {
            return param.getItems();
        } catch (Exception e) {
            return null;
        }
    }
}
