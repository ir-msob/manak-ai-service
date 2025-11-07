package ir.msob.manak.chat.client;

import ir.msob.jima.crud.api.restful.client.domain.DomainCrudWebClient;
import ir.msob.manak.core.model.jima.security.User;
import ir.msob.manak.domain.model.common.ServiceName;
import ir.msob.manak.domain.model.toolhub.dto.ToolRegistryDto;
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

    public Flux<ToolRegistryDto> getStream(User user) {
        return this.webClient.get()
                .uri(builder -> builder
                        .host(ServiceName.TOOL_HUB)
                        .path("/api/v1/registry")
                        .build())
                .headers(headers -> domainCrudWebClient.setDefaultHeaders(headers, user))
                .retrieve()
                .bodyToFlux(ToolRegistryDto.class)
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
