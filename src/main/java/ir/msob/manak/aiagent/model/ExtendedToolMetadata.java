package ir.msob.manak.aiagent.model;

import org.springframework.ai.tool.metadata.ToolMetadata;

public class ExtendedToolMetadata implements ToolMetadata {
    private final boolean returnDirect;
    private final String outputSchemaJson; // JSON schema as string (optional)
    private final String errorSchemaJson;  // JSON schema as string (optional)
    private final String version;

    private ExtendedToolMetadata(boolean returnDirect, String outputSchemaJson, String errorSchemaJson, String version) {
        this.returnDirect = returnDirect;
        this.outputSchemaJson = outputSchemaJson;
        this.errorSchemaJson = errorSchemaJson;
        this.version = version;
    }

    public static Builder builder() {
        return new Builder();
    }

    @Override
    public boolean returnDirect() {
        return returnDirect;
    }

    public String getOutputSchemaJson() {
        return outputSchemaJson;
    }

    public String getErrorSchemaJson() {
        return errorSchemaJson;
    }

    public String getVersion() {
        return version;
    }

    public static class Builder {
        private boolean returnDirect = false;
        private String outputSchemaJson;
        private String errorSchemaJson;
        private String version;

        public Builder returnDirect(boolean r) {
            this.returnDirect = r;
            return this;
        }

        public Builder outputSchemaJson(String s) {
            this.outputSchemaJson = s;
            return this;
        }

        public Builder errorSchemaJson(String s) {
            this.errorSchemaJson = s;
            return this;
        }

        public Builder version(String v) {
            this.version = v;
            return this;
        }

        public ExtendedToolMetadata build() {
            return new ExtendedToolMetadata(returnDirect, outputSchemaJson, errorSchemaJson, version);
        }
    }
}
