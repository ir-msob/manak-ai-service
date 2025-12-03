package ir.msob.manak.ai.embedding;

import ir.msob.jima.core.commons.filter.Filter;
import ir.msob.jima.core.commons.logger.Logger;
import ir.msob.jima.core.commons.logger.LoggerFactory;
import ir.msob.manak.ai.model.ModelProviderHubService;
import ir.msob.manak.ai.modelspecification.ModelSpecificationService;
import ir.msob.manak.core.model.jima.security.User;
import ir.msob.manak.domain.model.ai.embedding.EmbeddingRequestDto;
import ir.msob.manak.domain.model.ai.embedding.EmbeddingResponseDto;
import ir.msob.manak.domain.model.ai.modelspecification.ModelSpecification;
import ir.msob.manak.domain.model.ai.modelspecification.ModelSpecificationCriteria;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Mono;

@Service
@RequiredArgsConstructor
public class EmbeddingService {

    private static final Logger log = LoggerFactory.getLogger(EmbeddingService.class);

    private final ModelProviderHubService modelProviderHubService;
    private final ModelSpecificationService modelSpecificationService;

    public Mono<EmbeddingResponseDto> embedding(EmbeddingRequestDto dto, User user) {
        log.info("Starting embedding request. modelKey={}", dto.getModel());

        ModelSpecificationCriteria criteria = ModelSpecificationCriteria.builder()
                .key(Filter.eq(dto.getModel()))
                .build();

        return modelSpecificationService.getOne(criteria, user)
                .doOnSubscribe(sub -> log.debug("Fetching ModelSpecification for key={}", dto.getModel()))
                .doOnNext(spec -> log.info("ModelSpecification found. key={}, providerType={}", spec.getKey(), spec.getProviderType()))
                .map(ModelSpecification::getProviderType)
                .map(modelProviderHubService::getProvider)
                .doOnNext(provider -> log.info("Resolved ModelProvider: {}", provider.getClass().getSimpleName()))
                .flatMap(modelProviderService -> modelProviderService.embedding(dto, user))
                .doOnSubscribe(sub -> log.debug("Starting chat stream for modelKey={}", dto.getModel()))
                .doOnNext(chunk -> log.trace("Chat stream output: {}", chunk))
                .doOnError(e -> log.error("Error occurred during chat execution for modelKey={}: {}", dto.getModel(), e.getMessage(), e));
    }
}
