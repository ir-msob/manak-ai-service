package ir.msob.manak.aiagent.client;

import ir.msob.jima.core.beans.properties.JimaProperties;
import ir.msob.jima.core.commons.domain.DomainInfo;
import ir.msob.jima.crud.api.restful.client.domain.DomainCrudWebClient;
import ir.msob.manak.core.model.jima.security.User;
import ir.msob.manak.domain.model.toolhub.dto.ToolDto;
import ir.msob.manak.domain.model.toolhub.toolprovider.ToolProviderDto;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Flux;

@Component
@RequiredArgsConstructor
public class RegistryClient {

    private final DomainCrudWebClient domainCrudWebClient;
    private final WebClient webClient;
    private final JimaProperties jimaProperties;

    public Flux<ToolDto> getStream(User user) {
        DomainInfo domainInfo = DomainInfo.info.getAnnotation(ToolProviderDto.class);
        return this.webClient.get()
                .uri(builder -> builder
                        .host(domainInfo.serviceName())
                        .path("/api/v1/registry")
                        .build())
                .headers((builder) -> domainCrudWebClient.setDefaultHeaders(builder, user))
                .retrieve()
                .bodyToFlux(ToolDto.class);
    }
}
