package ir.msob.manak.aiagent.client;

import ir.msob.jima.core.commons.domain.DomainInfo;
import ir.msob.jima.crud.api.restful.client.domain.DomainCrudWebClient;
import ir.msob.manak.core.model.jima.security.User;
import ir.msob.manak.domain.model.toolhub.dto.InvokeRequest;
import ir.msob.manak.domain.model.toolhub.dto.InvokeResponse;
import ir.msob.manak.domain.model.toolhub.toolprovider.ToolProviderDto;
import ir.msob.manak.domain.service.toolhub.util.ToolExecutorUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

@Component
@RequiredArgsConstructor
@Slf4j
public class GatewayClient {

    private final DomainCrudWebClient domainCrudWebClient;
    private final WebClient webClient;

    public Mono<InvokeResponse> invoke(InvokeRequest dto, User user) {
        DomainInfo domainInfo = DomainInfo.info.getAnnotation(ToolProviderDto.class);

        return this.webClient.post()
                .uri(builder -> builder
                        .host(domainInfo.serviceName())
                        .path("/api/v1/gateway/invoke")
                        .build())
                .headers(headers -> domainCrudWebClient.setDefaultHeaders(headers, user))
                .bodyValue(dto)
                .retrieve()
                .bodyToMono(InvokeResponse.class)
                .doOnSubscribe(sub -> log.info("Invoking tool via gateway: toolId={}, user={}", dto.getToolId(), user.getId()))
                .doOnSuccess(res -> log.info("Tool invocation successful: toolId={}, response={}", dto.getToolId(), res))
                .doOnError(e -> log.error("Error invoking tool via gateway: toolId={}, error={}", dto.getToolId(), e.getMessage(), e))
                .onErrorResume(e -> {
                    String errorMsg = ToolExecutorUtil.buildErrorResponse(dto.getToolId(), e);
                    InvokeResponse errorResponse = new InvokeResponse();
                    errorResponse.setToolId(dto.getToolId());
                    errorResponse.setError(errorMsg);
                    return Mono.just(errorResponse);
                });
    }
}
