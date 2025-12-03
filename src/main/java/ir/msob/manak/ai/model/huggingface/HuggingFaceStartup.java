package ir.msob.manak.ai.model.huggingface;

import ir.msob.jima.core.commons.filter.Filter;
import ir.msob.jima.core.commons.logger.Logger;
import ir.msob.jima.core.commons.logger.LoggerFactory;
import ir.msob.manak.ai.model.ModelEntry;
import ir.msob.manak.ai.modelspecification.ModelSpecificationService;
import ir.msob.manak.core.service.jima.security.UserService;
import ir.msob.manak.domain.model.ai.modelspecification.ModelSpecification;
import ir.msob.manak.domain.model.ai.modelspecification.ModelSpecificationCriteria;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import org.springframework.ai.huggingface.HuggingfaceChatModel;
import org.springframework.stereotype.Component;

import static ir.msob.manak.ai.model.ModelProviderHubService.HUGGING_FACE_TYPE;

@Component
@RequiredArgsConstructor
public class HuggingFaceStartup {
    private static final Logger log = LoggerFactory.getLogger(HuggingFaceStartup.class);

    private final HuggingFaceRegistry hfRegistry;
    private final ModelSpecificationService modelSpecificationService;
    private final UserService userService;

    @PostConstruct
    public void startup() {
        ModelSpecificationCriteria criteria = ModelSpecificationCriteria.builder()
                .providerType(Filter.eq(HUGGING_FACE_TYPE))
                .build();

        modelSpecificationService.getStream(criteria, userService.getSystemUser())
                .doOnNext(spec -> {
                    try {


                        if (spec.getModelTypes().contains(ModelSpecification.ModelType.CHAT)) {
                            HuggingfaceChatModel chatModel = new HuggingfaceChatModel("", spec.getBaseUrl());

                            hfRegistry.getChatModels().add(ModelEntry.<HuggingfaceChatModel>builder()
                                    .key(spec.getKey())
                                    .modelTypes(spec.getModelTypes())
                                    .model(chatModel)
                                    .build());
                        } else if (spec.getModelTypes().contains(ModelSpecification.ModelType.EMBEDDING)) {

                        }

                        log.info("Loaded HuggingFace model for key {}", spec.getKey());


                    } catch (Exception e) {
                        log.error("Error creating HuggingFace model for specification: {}", spec, e);
                    }
                })
                .doOnComplete(() -> log.info("Loaded HuggingFace {} chat models and {} embedding models from database", hfRegistry.getChatModels().size(), hfRegistry.getEmbeddingModels().size()))
                .subscribe();
    }
}
