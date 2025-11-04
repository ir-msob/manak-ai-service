package ir.msob.manak.aiagent.client;

import ir.msob.jima.core.commons.domain.DomainInfo;
import ir.msob.jima.crud.api.restful.client.domain.DomainCrudWebClient;
import ir.msob.manak.core.model.jima.security.User;
import ir.msob.manak.domain.model.toolhub.dto.ToolDto;
import ir.msob.manak.domain.model.toolhub.toolprovider.ToolProviderDto;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Flux;

@Component
@RequiredArgsConstructor
@Slf4j
public class RegistryClient {

    private final DomainCrudWebClient domainCrudWebClient;
    private final WebClient webClient;

    public Flux<ToolDto> getStream(User user) {
        DomainInfo domainInfo = DomainInfo.info.getAnnotation(ToolProviderDto.class);

        return this.webClient.get()
                .uri(builder -> builder
                        .host(domainInfo.serviceName())
                        .path("/api/v1/registry")
                        .build())
                .headers(headers -> domainCrudWebClient.setDefaultHeaders(headers, user))
                .retrieve()
                .bodyToFlux(ToolDto.class)
                .doOnSubscribe(sub -> log.info("Requesting tool registry stream"))
                .doOnNext(tool -> log.debug("Received tool from registry stream: id={}, version={}", tool.getToolId(), tool.getVersion()))
                .doOnComplete(() -> log.info("Completed receiving tool registry stream"))
                .doOnError(e -> log.error("Error while streaming tool registry: {}", e.getMessage(), e))
                .onErrorResume(e -> {
                    log.warn("Returning empty tool stream due to error: {}", e.getMessage());
                    return Flux.empty();
                });
    }
}
