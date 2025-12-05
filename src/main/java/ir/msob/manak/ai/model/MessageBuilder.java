package ir.msob.manak.ai.model;

import ir.msob.manak.domain.model.ai.chat.ChatRequestDto;
import ir.msob.manak.domain.model.ai.chat.ChatRequestDto.Message;
import ir.msob.manak.domain.model.ai.chat.ChatRequestDto.TemplateRef;
import org.apache.logging.log4j.util.Strings;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.messages.AssistantMessage;
import org.springframework.ai.chat.prompt.DefaultChatOptions;

import java.util.Map;

public class MessageBuilder {

    private final ChatRequestDto request;

    public MessageBuilder(ChatRequestDto request) {
        this.request = request;
    }

    public void buildMessage(ChatClient.ChatClientRequestSpec spec) {
        Map<String, Object> vars = request.getTemplateVariables() == null ? Map.of() : request.getTemplateVariables();
        Map<ChatRequestDto.Role, TemplateRef> templates = request.getTemplates();

        // Apply templates (SYSTEM / USER / DEVELOPER) if present
        if (templates != null && !templates.isEmpty()) {
            applyTemplates(spec, templates, vars);
        }

        // Apply role-based messages if present in request
        if (request.getMessages() != null && !request.getMessages().isEmpty()) {
            applyRoleBasedMessages(spec, vars);
        } else {
            // Fallback to simpleMessage if no role messages
            fallbackToSimpleMessage(spec, vars);
        }

        // Apply options (temperature, max tokens, etc.)
        applyOptions(spec);
    }

    private void applyTemplates(ChatClient.ChatClientRequestSpec spec, Map<ChatRequestDto.Role, TemplateRef> templates, Map<String, Object> vars) {
        // system template
        if (templates.containsKey(ChatRequestDto.Role.SYSTEM)) {
            String systemTemplate = resolveTemplate(templates.get(ChatRequestDto.Role.SYSTEM));
            spec.system(promptSystemSpec -> promptSystemSpec.text(systemTemplate).params(vars));
        }
        // assistant template
        if (templates.containsKey(ChatRequestDto.Role.ASSISTANT)) {
            String assistantTemplate = resolveTemplate(templates.get(ChatRequestDto.Role.ASSISTANT));
            spec.messages(AssistantMessage.builder()
                    .content(assistantTemplate)
                    .properties(vars)
                    .build());
        }
        // user template (if present and no role-based messages)
        if (templates.containsKey(ChatRequestDto.Role.USER)) {
            String userTemplate = resolveTemplate(templates.get(ChatRequestDto.Role.USER));
            spec.user(promptUserSpec -> promptUserSpec.text(userTemplate).params(vars));
        }
    }

    private void applyRoleBasedMessages(ChatClient.ChatClientRequestSpec spec, Map<String, Object> vars) {
        for (Message m : request.getMessages()) {
            if (m == null) continue;
            String content = m.getContent();
            ChatRequestDto.Role role = m.getRole() == null ? ChatRequestDto.Role.USER : m.getRole();
            switch (role) {
                case SYSTEM -> {
                    spec.system(promptSystemSpec -> promptSystemSpec.text(content).params(vars));
                }
                case ASSISTANT -> {
                    spec.messages(AssistantMessage.builder()
                            .content(content)
                            .properties(vars)
                            .build());
                }
                case USER -> {
                    spec.user(promptUserSpec -> promptUserSpec.text(content).params(vars));
                }
            }
        }
    }

    private void fallbackToSimpleMessage(ChatClient.ChatClientRequestSpec spec, Map<String, Object> vars) {
        boolean userTemplateUsed = request.getTemplates() != null && request.getTemplates().containsKey(ChatRequestDto.Role.USER);
        if (!userTemplateUsed && Strings.isNotBlank(request.getSimpleMessage())) {
            spec.user(promptUserSpec -> promptUserSpec.text(request.getSimpleMessage()).params(vars));
        }
    }

    private void applyOptions(ChatClient.ChatClientRequestSpec spec) {
        if (request.getOptions() != null) {
            DefaultChatOptions chatOptions = new DefaultChatOptions();
            chatOptions.setModel(request.getModel());

            if (request.getOptions().getTemperature() != null)
                chatOptions.setTemperature(request.getOptions().getTemperature());
            if (request.getOptions().getMaxTokens() != null)
                chatOptions.setMaxTokens(request.getOptions().getMaxTokens());
            if (request.getOptions().getTopP() != null)
                chatOptions.setTopP(request.getOptions().getTopP());
            if (request.getOptions().getTopK() != null)
                chatOptions.setTopK(request.getOptions().getTopK());
            if (request.getOptions().getPresencePenalty() != null)
                chatOptions.setPresencePenalty(request.getOptions().getPresencePenalty());
            if (request.getOptions().getFrequencyPenalty() != null)
                chatOptions.setFrequencyPenalty(request.getOptions().getFrequencyPenalty());
            spec.options(chatOptions);
        }
    }

    private String resolveTemplate(TemplateRef ref) {
        if (ref == null) return null;
        if (ref.getType() == null) throw new IllegalArgumentException("TemplateRef.type must not be null");
        switch (ref.getType()) {
            case INLINE -> {
                return ref.getContent();
            }
            case BASE64 -> {
                byte[] decoded = java.util.Base64.getDecoder().decode(ref.getContent());
                return new String(decoded);
            }
            default ->
                    throw new IllegalArgumentException("Only INLINE and BASE64 TemplateRef types are supported. Found: " + ref.getType());
        }
    }
}
