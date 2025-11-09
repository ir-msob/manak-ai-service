package ir.msob.manak.chat.model;

import ir.msob.manak.chat.client.GatewayClient;
import ir.msob.manak.core.service.jima.security.UserService;
import ir.msob.manak.domain.model.toolhub.dto.InvokeRequest;
import ir.msob.manak.domain.model.toolhub.dto.InvokeResponse;
import ir.msob.manak.domain.service.toolhub.util.ToolExecutorUtil;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Mono;

import java.time.Instant;
import java.util.Arrays;
import java.util.Map;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class ToolInvoker {
    private static final Logger log = LoggerFactory.getLogger(ToolInvoker.class);

    private final GatewayClient gatewayClient;
    private final UserService userService;

    public Object invoke(String toolId, Map<String, Object> params) {
        InvokeRequest request = InvokeRequest.builder()
                .id(UUID.randomUUID().toString())
                .toolId(toolId)
                .parameters(params)
                .build();
        try {
            log.debug("Invoking tool '{}'", toolId);

            return gatewayClient.invoke(request, userService.getSystemUser())
                    .map(this::extractResponse)
                    .onErrorResume(e -> {
                        log.error("Error invoking tool '{}': {}", toolId, e.getMessage(), e);
                        return Mono.just(buildErrorResponse(request, e));
                    })
                    .toFuture()
                    .get();
        } catch (Exception e) {
            log.error("Unexpected error invoking tool '{}': {}", toolId, e.getMessage(), e);
            return buildErrorResponse(request, e);
        }
    }

    private InvokeResponse buildErrorResponse(InvokeRequest dto, Throwable e) {
        String toolId = dto.getToolId();
        String formattedMessage = ToolExecutorUtil.buildErrorResponse(toolId, e);

        return InvokeResponse.builder()
                .id(dto.getId())
                .toolId(toolId)
                .error(InvokeResponse.ErrorInfo.builder()
                        .code("EXECUTION_ERROR")
                        .message(formattedMessage)
                        .stackTrace(Arrays.toString(e.getStackTrace()))
                        .details(dto.getParameters())
                        .build())
                .executedAt(Instant.now())
                .build();
    }

    private Object extractResponse(InvokeResponse response) {
        if (response == null) {
            return "No response received from tool.";
        }
        if (response.getError() != null) {
            return response.getError();
        }
        return response.getResult();
    }
}

