package ir.msob.manak.chat.model.huggingface;

import ir.msob.jima.core.commons.filter.Filter;
import ir.msob.jima.core.commons.logger.Logger;
import ir.msob.jima.core.commons.logger.LoggerFactory;
import ir.msob.manak.chat.modelspecification.ModelSpecificationService;
import ir.msob.manak.core.service.jima.security.UserService;
import ir.msob.manak.domain.model.chat.modelspecification.ModelSpecificationCriteria;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import org.springframework.ai.huggingface.HuggingfaceChatModel;
import org.springframework.stereotype.Component;

import static ir.msob.manak.chat.model.ModelProviderHubService.HUGGING_FACE_TYPE;

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
                .type(Filter.eq(HUGGING_FACE_TYPE))
                .build();

        modelSpecificationService.getStream(criteria, userService.getSystemUser())
                .doOnNext(spec -> {
                    try {

                        HuggingfaceChatModel chatModel = new HuggingfaceChatModel("", spec.getBaseUrl());

                        hfRegistry.getModels().put(spec.getKey(), chatModel);
                        log.info("Loaded HuggingFace model for key {}", spec.getKey());

                    } catch (Exception e) {
                        log.error("Error creating HuggingFace model for specification: {}", spec, e);
                    }
                })
                .doOnComplete(() -> log.info("Loaded {} HuggingFace models", hfRegistry.getModels().size()))
                .subscribe();
    }
}
