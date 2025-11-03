package ir.msob.manak.aiagent.model;

import ir.msob.manak.aiagent.client.GatewayClient;
import ir.msob.manak.core.service.jima.security.UserService;
import ir.msob.manak.domain.model.toolhub.dto.InvokeRequest;
import lombok.RequiredArgsConstructor;
import lombok.SneakyThrows;
import org.apache.logging.log4j.util.Strings;
import org.springframework.stereotype.Service;

import java.io.Serializable;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class Invoker {
    private final GatewayClient gatewayClient;
    private final UserService userService;

    @SneakyThrows
    public Serializable invoke(String toolId, Map<String, Serializable> params) {
        InvokeRequest request = InvokeRequest.builder()
                .toolId(toolId)
                .params(params)
                .build();
        return gatewayClient.invoke(request, userService.getSystemUser())
                .map(invokeResponse -> Strings.isBlank(invokeResponse.getError()) ? invokeResponse.getRes() : invokeResponse.getError())
                .toFuture()
                .get();
    }
}
