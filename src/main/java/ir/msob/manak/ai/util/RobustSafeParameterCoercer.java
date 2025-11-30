package ir.msob.manak.ai.util;

import com.fasterxml.jackson.databind.ObjectMapper;
import ir.msob.manak.domain.model.common.model.ParameterDescriptor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.regex.Pattern;

/**
 * RobustSafeParameterCoercer
 * <p>
 * Reworked to use {@link ParameterDescriptor} (the new parameter model).
 * Behavior and heuristics are preserved from the original implementation,
 * but method names and schema accessors were adapted for the new model.
 */
public record RobustSafeParameterCoercer(ObjectMapper mapper) {
    private static final Logger log = LoggerFactory.getLogger(RobustSafeParameterCoercer.class);

    private static final int MAX_JSON_UNWRAP_DEPTH = 4;
    private static final Pattern ONLY_DIGITS = Pattern.compile("^-?\\d+$");
    private static final Pattern DECIMAL_OR_SCI = Pattern.compile("^-?\\d*[.,]?\\d+(?:[eE][+-]?\\d+)?$");
    private static final Pattern HEX_PATTERN = Pattern.compile("^0x[0-9a-fA-F]+$");

    public Map<String, Object> coerce(Map<String, Object> input, Map<String, ParameterDescriptor> schema) {
        if (input == null) return Collections.emptyMap();
        if (schema == null || schema.isEmpty()) return new HashMap<>(input);

        Map<String, Object> out = new LinkedHashMap<>();

        // First coerce schema-declared keys
        for (Map.Entry<String, ParameterDescriptor> e : schema.entrySet()) {
            String key = e.getKey();
            ParameterDescriptor def = e.getValue();
            Object raw = input.get(key);

            if (raw == null) {
                out.put(key, def == null ? null : def.getDefaultValue());
                continue;
            }

            Object coerced = coerceWithAllHeuristics(raw, def);
            out.put(key, coerced);
        }

        // Preserve extra keys as-is (non-destructive)
        for (Map.Entry<String, Object> e : input.entrySet()) {
            out.putIfAbsent(e.getKey(), e.getValue());
        }

        return out;
    }

    private Object coerceWithAllHeuristics(Object raw, ParameterDescriptor def) {
        try {
            // Direct attempt
            Object direct = tryCoerceDirect(raw, def);
            if (matchesType(direct, def)) return direct;

            // If raw is String, try many unwrapping/decoding strategies
            if (raw instanceof String) {
                String s = ((String) raw).trim();

                // URL-decoded attempt
                String urlDecoded = tryUrlDecodeIfNeeded(s);
                if (!Objects.equals(urlDecoded, s)) {
                    Object parsed = tryParseJsonRecursive(urlDecoded, 0);
                    if (parsed != null) {
                        Object after = tryCoerceDirect(parsed, def);
                        if (matchesType(after, def)) return after;
                    }
                }

                // base64 JSON attempt
                Object b64 = tryBase64JsonDecode(s);
                if (b64 != null) {
                    Object after = tryCoerceDirect(b64, def);
                    if (matchesType(after, def)) return after;
                }

                // JSON unwrapping
                Object parsed = tryParseJsonRecursive(s, 0);
                if (parsed != null && !Objects.equals(parsed, s)) {
                    Object after = tryCoerceDirect(parsed, def);
                    if (matchesType(after, def)) return after;
                }

                // CSV-like -> array fallback
                if (def != null && def.getType() != null && def.getType() == ParameterDescriptor.ToolParameterType.ARRAY) {
                    Object arr = coerceToArray(raw, def.getItems());
                    if (matchesType(arr, def)) return arr;
                }

                // numeric normalization
                if (def != null && def.getType() != null && def.getType() == ParameterDescriptor.ToolParameterType.NUMBER) {
                    Number n = normalizeAndParseNumber(s);
                    if (n != null) return n;
                }
            }

            // structural conversions
            if (def != null && def.getType() == ParameterDescriptor.ToolParameterType.ARRAY && raw instanceof Map<?, ?>) {
                Object fromMap = tryConvertNumericKeyedMapToList((Map<?, ?>) raw, def.getItems());
                if (matchesType(fromMap, def)) return fromMap;
            }

            if (def != null && def.getType() == ParameterDescriptor.ToolParameterType.OBJECT && raw instanceof List<?>) {
                Object converted = tryConvertArrayToMap((List<?>) raw, def.getProperties());
                if (matchesType(converted, def)) return converted;
            }

            // fallback: original raw
            return raw;
        } catch (Exception ex) {
            log.debug("Unexpected exception in coercion heuristics for raw='{}': {}", raw, ex.getMessage());
            return raw;
        }
    }

    private Object tryCoerceDirect(Object raw, ParameterDescriptor def) {
        if (def == null || def.getType() == null) return raw;

        return switch (def.getType()) {
            case STRING -> coerceToString(raw);
            case NUMBER -> {
                Number n = coerceToNumber(raw);
                yield n != null ? n : raw;
            }
            case BOOLEAN -> {
                Boolean b = coerceToBoolean(raw);
                yield b != null ? b : raw;
            }
            case ARRAY -> coerceToArray(raw, def.getItems());
            case OBJECT -> coerceToObject(raw, def.getProperties());
        };
    }

    private String coerceToString(Object raw) {
        try {
            if (raw == null) return null;
            if (raw instanceof String) return (String) raw;
            return mapper.writeValueAsString(raw);
        } catch (Exception e) {
            try {
                return String.valueOf(raw);
            } catch (Exception ex) {
                return null;
            }
        }
    }

    private Number coerceToNumber(Object raw) {
        try {
            if (raw instanceof Number) return (Number) raw;
            if (raw == null) return null;

            String s = String.valueOf(raw).trim();
            if (s.isEmpty() || s.equalsIgnoreCase("null") || s.equalsIgnoreCase("none")) return null;

            if (HEX_PATTERN.matcher(s).matches()) {
                try {
                    return Long.parseLong(s.substring(2), 16);
                } catch (Exception ignored) {
                }
            }

            if (ONLY_DIGITS.matcher(s).matches()) {
                try {
                    return Long.parseLong(s);
                } catch (Exception ignored) {
                }
            }

            if (DECIMAL_OR_SCI.matcher(s.replace(",", ".")).matches()) {
                try {
                    return Double.parseDouble(s.replace(",", "."));
                } catch (Exception ignored) {
                }
            }

            String cleaned = s.replaceAll("(?<=\\d),(?=\\d{3}\\b)", "");
            try {
                if (ONLY_DIGITS.matcher(cleaned).matches()) return Long.parseLong(cleaned);
                return Double.parseDouble(cleaned);
            } catch (Exception ignored) {
            }

            return null;
        } catch (Exception e) {
            return null;
        }
    }

    private Boolean coerceToBoolean(Object raw) {
        try {
            if (raw instanceof Boolean) return (Boolean) raw;
            if (raw == null) return null;
            String s = String.valueOf(raw).trim().toLowerCase(Locale.ROOT);
            if (s.isEmpty() || s.equalsIgnoreCase("null") || s.equalsIgnoreCase("none")) return null;
            if (Arrays.asList("true", "1", "yes", "y", "on", "t").contains(s)) return Boolean.TRUE;
            if (Arrays.asList("false", "0", "no", "n", "off", "f").contains(s)) return Boolean.FALSE;
            return null;
        } catch (Exception e) {
            return null;
        }
    }

    private Object coerceToArray(Object raw, ParameterDescriptor itemSchema) {
        try {
            List<Object> list;

            switch (raw) {
                case List<?> objects -> list = new ArrayList<>(objects);
                case String string -> {
                    String s = string.trim();
                    if (s.isEmpty() || s.equalsIgnoreCase("null") || s.equalsIgnoreCase("none")) return List.of();

                    Object parsed = tryParseJsonRecursive(s, 0);
                    if (parsed instanceof List<?>) {
                        list = new ArrayList<>((List<?>) parsed);
                    } else {
                        String cleaned = s.replaceAll("^\\[|]$", "")
                                .replaceAll("^['\"]+|['\"]+$", "")
                                .trim();
                        if (cleaned.isEmpty()) {
                            list = List.of();
                        } else {
                            String[] parts = cleaned.contains(",") ? cleaned.split("\\s*,\\s*") : cleaned.split("\\s+");
                            list = new ArrayList<>(Arrays.asList(parts));
                        }
                    }
                }
                case null, default -> {
                    list = new ArrayList<>();
                    list.add(raw);
                }
            }

            if (itemSchema != null) {
                List<Object> coerced = new ArrayList<>();
                for (Object item : list) coerced.add(coerceWithAllHeuristics(item, itemSchema));
                return coerced;
            }
            return list;
        } catch (Exception e) {
            log.debug("coerceToArray failed for '{}': {}", raw, e.getMessage());
            return raw;
        }
    }

    private Object coerceToObject(Object raw, Map<String, ParameterDescriptor> properties) {
        try {
            Map<String, Object> map;

            switch (raw) {
                case Map<?, ?> map1 -> {
                    map = new LinkedHashMap<>();
                    map1.forEach((k, v) -> map.put(String.valueOf(k), v));
                }
                case String string -> {
                    String s = string.trim();
                    if (s.isEmpty() || s.equalsIgnoreCase("null") || s.equalsIgnoreCase("none")) return Map.of();
                    Object parsed = tryParseJsonRecursive(s, 0);
                    if (parsed instanceof Map<?, ?>) {
                        map = new LinkedHashMap<>();
                        ((Map<?, ?>) parsed).forEach((k, v) -> map.put(String.valueOf(k), v));
                    } else {
                        return raw;
                    }
                }
                case List<?> objects -> {
                    Object converted = tryConvertArrayToMap(objects, properties);
                    if (converted instanceof Map<?, ?>) return converted;
                    return raw;
                }
                case null, default -> {
                    return raw;
                }
            }

            if (properties != null && !properties.isEmpty()) {
                return coerce(map, properties);
            }
            return map;
        } catch (Exception e) {
            log.debug("coerceToObject failed for '{}': {}", raw, e.getMessage());
            return raw;
        }
    }

    private Object tryParseJsonRecursive(String s, int depth) {
        if (s == null) return null;
        if (depth >= MAX_JSON_UNWRAP_DEPTH) return null;
        String trimmed = s.trim();

        try {
            Object parsed = null;
            try {
                parsed = mapper.readValue(trimmed, Object.class);
            } catch (Exception ignored) {
                if (trimmed.startsWith("\"") && trimmed.endsWith("\"") && trimmed.length() >= 2) {
                    String unquoted = trimmed.substring(1, trimmed.length() - 1)
                            .replace("\\\"", "\"")
                            .replace("\\\\", "\\");
                    try {
                        parsed = mapper.readValue(unquoted, Object.class);
                    } catch (Exception ignored2) {
                    }
                }
            }

            if (parsed instanceof String) {
                String inner = ((String) parsed).trim();
                if ((inner.startsWith("{") && inner.endsWith("}")) || (inner.startsWith("[") && inner.endsWith("]"))) {
                    return tryParseJsonRecursive(inner, depth + 1);
                }
            }
            return parsed;
        } catch (Exception e) {
            log.debug("tryParseJsonRecursive failed for '{}': {}", s, e.getMessage());
            return null;
        }
    }

    private Object tryBase64JsonDecode(String s) {
        try {
            String candidate = s.trim();
            if (candidate.length() < 8) return null;
            if (candidate.startsWith("base64,")) candidate = candidate.substring(7);

            try {
                byte[] decoded = Base64.getDecoder().decode(candidate);
                String asString = new String(decoded, StandardCharsets.UTF_8).trim();
                if ((asString.startsWith("{") && asString.endsWith("}")) || (asString.startsWith("[") && asString.endsWith("]"))) {
                    return mapper.readValue(asString, Object.class);
                }
            } catch (IllegalArgumentException ignored) {
            }
            return null;
        } catch (Exception e) {
            return null;
        }
    }

    private String tryUrlDecodeIfNeeded(String s) {
        try {
            if (s.contains("%7B") || s.contains("%5B") || s.contains("%22")) {
                try {
                    return URLDecoder.decode(s, StandardCharsets.UTF_8);
                } catch (Exception ignored) {
                }
            }
            return s;
        } catch (Exception e) {
            return s;
        }
    }

    private Object tryConvertNumericKeyedMapToList(Map<?, ?> map, ParameterDescriptor itemSchema) {
        try {
            TreeMap<Integer, Object> ordered = new TreeMap<>();
            boolean anyNumeric = false;
            for (Map.Entry<?, ?> e : map.entrySet()) {
                String keyStr = String.valueOf(e.getKey());
                try {
                    int idx = Integer.parseInt(keyStr);
                    anyNumeric = true;
                    ordered.put(idx, e.getValue());
                } catch (NumberFormatException ignored) {
                }
            }
            if (!anyNumeric) return null;
            List<Object> list = new ArrayList<>(ordered.values());
            if (itemSchema != null) {
                List<Object> coerced = new ArrayList<>();
                for (Object item : list) coerced.add(coerceWithAllHeuristics(item, itemSchema));
                return coerced;
            }
            return list;
        } catch (Exception e) {
            return null;
        }
    }

    private Object tryConvertArrayToMap(List<?> list, Map<String, ParameterDescriptor> propertiesSchema) {
        try {
            Map<String, Object> result = new LinkedHashMap<>();
            boolean converted = false;
            for (Object item : list) {
                if (item instanceof List<?> pair) {
                    if (pair.size() >= 2) {
                        String k = String.valueOf(pair.get(0));
                        Object v = pair.get(1);
                        result.put(k, v);
                        converted = true;
                        continue;
                    }
                }
                if (item instanceof Map<?, ?> m) {
                    if (m.size() == 1) {
                        Map.Entry<?, ?> en = m.entrySet().iterator().next();
                        result.put(String.valueOf(en.getKey()), en.getValue());
                    } else {
                        if (m.containsKey("key") && m.containsKey("value")) {
                            result.put(String.valueOf(m.get("key")), m.get("value"));
                            converted = true;
                            continue;
                        }
                        m.forEach((k, v) -> result.put(String.valueOf(k), v));
                    }
                    converted = true;
                }
            }

            if (!converted) return null;
            if (propertiesSchema != null && !propertiesSchema.isEmpty()) {
                return coerce(result, propertiesSchema);
            }
            return result;
        } catch (Exception e) {
            return null;
        }
    }

    private Number normalizeAndParseNumber(String s) {
        try {
            if (s == null) return null;
            String trimmed = s.trim();
            if (trimmed.isEmpty()) return null;

            if (HEX_PATTERN.matcher(trimmed).matches()) {
                try {
                    return Long.parseLong(trimmed.substring(2), 16);
                } catch (Exception ignored) {
                }
            }

            if (trimmed.contains(",") && trimmed.contains(".")) {
                int lastComma = trimmed.lastIndexOf(',');
                int lastDot = trimmed.lastIndexOf('.');
                if (lastDot > lastComma) {
                    trimmed = trimmed.replace(",", "");
                } else {
                    trimmed = trimmed.replace(".", "").replace(",", ".");
                }
            } else {
                trimmed = trimmed.replaceAll("(?<=\\d),(?=\\d{3}\\b)", "");
                if (trimmed.matches(".*,\\d+$") && !trimmed.contains(".")) {
                    trimmed = trimmed.replace(',', '.');
                }
            }

            if (ONLY_DIGITS.matcher(trimmed).matches()) {
                try {
                    return Long.parseLong(trimmed);
                } catch (Exception ignored) {
                }
            }
            try {
                return Double.parseDouble(trimmed);
            } catch (Exception ignored) {
            }
            return null;
        } catch (Exception e) {
            return null;
        }
    }

    private boolean matchesType(Object value, ParameterDescriptor def) {
        if (def == null || def.getType() == null) return false;
        return switch (def.getType()) {
            case STRING -> value instanceof String;
            case NUMBER -> value instanceof Number;
            case BOOLEAN -> value instanceof Boolean;
            case ARRAY -> value instanceof List<?>;
            case OBJECT -> value instanceof Map<?, ?>;
        };
    }
}
