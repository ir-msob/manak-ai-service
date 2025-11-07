package ir.msob.manak.chat.model;

import ir.msob.manak.chat.client.GatewayClient;
import ir.msob.manak.core.service.jima.security.UserService;
import ir.msob.manak.domain.model.toolhub.dto.InvokeRequest;
import ir.msob.manak.domain.model.toolhub.dto.InvokeResponse;
import ir.msob.manak.domain.service.toolhub.util.ToolExecutorUtil;
import lombok.RequiredArgsConstructor;
import org.apache.logging.log4j.util.Strings;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Mono;

import java.util.Map;

@Service
@RequiredArgsConstructor
public class ToolInvoker {
    private static final Logger log = LoggerFactory.getLogger(ToolInvoker.class);

    private final GatewayClient gatewayClient;
    private final UserService userService;

    public Object invoke(String toolId, Map<String, Object> params) {
        try {
            InvokeRequest request = InvokeRequest.builder()
                    .toolId(toolId)
                    .params(params)
                    .build();

            log.debug("Invoking tool '{}'", toolId);

            return gatewayClient.invoke(request, userService.getSystemUser())
                    .map(this::extractResponse)
                    .onErrorResume(e -> {
                        log.error("Error invoking tool '{}': {}", toolId, e.getMessage(), e);
                        return Mono.just((Object) ToolExecutorUtil.buildErrorResponse(toolId, e));
                    })
                    .toFuture()
                    .get();
        } catch (Exception e) {
            log.error("Unexpected error invoking tool '{}': {}", toolId, e.getMessage(), e);
            return ToolExecutorUtil.buildErrorResponse(toolId, e);
        }
    }

    private Object extractResponse(InvokeResponse response) {
        if (response == null) {
            return "No response received from tool.";
        }
        if (Strings.isNotBlank(response.getError())) {
            return response.getError();
        }
        return response.getRes();
    }
}
