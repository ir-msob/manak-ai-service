package ir.msob.manak.aiagent.util;

import com.fasterxml.jackson.databind.ObjectMapper;
import ir.msob.manak.domain.model.toolhub.toolprovider.tooldescriptor.ToolParameter;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.io.Serializable;
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
    public String exampleForSchema(Map<String, ToolParameter> inputSchema) {
        Map<String, Object> example = new LinkedHashMap<>();
        if (inputSchema != null) {
            for (Map.Entry<String, ToolParameter> e : inputSchema.entrySet()) {
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
    public String exampleForSchema(ToolParameter rootParam) {
        Object example = buildExampleValue(rootParam);
        try {
            return objectMapper.writeValueAsString(example); // compact
        } catch (Exception ex) {
            throw new RuntimeException("Failed to serialize example for root param", ex);
        }
    }

    // ------------ helper methods (unchanged) ------------

    private Map<String, Object> buildParameterSchemaMap(ToolParameter param) {
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
            Map<String, ToolParameter> props = safeGetProperties(param);
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
            ToolParameter items = safeGetItems(param);
            if (items != null) schema.put("items", buildParameterSchemaMap(items));
            else schema.put("items", Collections.singletonMap("type", "string"));
        } else {
            schema.put("type", jsonType);
        }

        if (param.getDescription() != null) schema.put("description", param.getDescription());
        if (param.getExample() != null) schema.put("example", param.getExample());
        if (param.getDefaultValue() != null) schema.put("default", param.getDefaultValue());

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
        if (param.getExample() != null) schema.put("examples", Collections.singletonList(param.getExample()));

        return schema;
    }

    private Object buildExampleValue(ToolParameter param) {
        if (param == null) return null;

        Object ex = param.getExample();
        if (ex != null) return ex;

        Object def = param.getDefaultValue();
        if (def != null) return def;

        String jsonType = detectJsonType(param);
        switch (jsonType) {
            case "string":
                return param.getDescription() != null ? shortFromDescription(param.getDescription()) : "string_example";
            case "integer":
                return 0;
            case "number":
                return 0.0;
            case "boolean":
                return false;
            case "array": {
                ToolParameter items = safeGetItems(param);
                Object itemExample = buildExampleValue(items != null ? items : dummyStringParam());
                return Collections.singletonList(itemExample);
            }
            case "object": {
                Map<String, ToolParameter> props = safeGetProperties(param);
                Map<String, Object> map = new LinkedHashMap<>();
                if (props != null) {
                    for (Map.Entry<String, ToolParameter> e : props.entrySet()) {
                        map.put(e.getKey(), buildExampleValue(e.getValue()));
                    }
                }
                return map;
            }
            default:
                return "string_example";
        }
    }

    private String shortFromDescription(String desc) {
        if (desc == null) return "string_example";
        int idx = desc.indexOf('.');
        String s = idx > 0 ? desc.substring(0, idx) : desc;
        s = s.trim();
        if (s.length() > 20) s = s.substring(0, 20).trim();
        return s.replaceAll("[^A-Za-z0-9_\\-]", "_");
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

    private ToolParameter dummyStringParam() {
        return new ToolParameter() {
            @Override
            public ToolParameterType getType() {
                return ToolParameterType.STRING;
            }

            @Override
            public String getDescription() {
                return "item";
            }

            @Override
            public Serializable getDefaultValue() {
                return null;
            }

            @Override
            public Serializable getExample() {
                return null;
            }

            @Override
            public boolean isRequired() {
                return false;
            }

            @Override
            public ToolParameter getItems() {
                return null;
            }

            @Override
            public Map<String, ToolParameter> getProperties() {
                return null;
            }
        };
    }
}
