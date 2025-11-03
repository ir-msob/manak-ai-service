package ir.msob.manak.aiagent.ai;

import ir.msob.jima.core.commons.filter.Filter;
import ir.msob.manak.aiagent.model.ModelProviderHubService;
import ir.msob.manak.aiagent.modelspecification.ModelSpecificationService;
import ir.msob.manak.core.model.jima.security.User;
import ir.msob.manak.domain.model.aiagent.chat.ChatRequest;
import ir.msob.manak.domain.model.aiagent.modelspecification.ModelSpecification;
import ir.msob.manak.domain.model.aiagent.modelspecification.ModelSpecificationCriteria;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;

@Service
@RequiredArgsConstructor
public class ChatService {
    private final ModelProviderHubService modelProviderHubService;
    private final ModelSpecificationService modelSpecificationService;

    public Flux<String> chat(ChatRequest dto, User user) {
        ModelSpecificationCriteria criteria = ModelSpecificationCriteria.builder()
                .key(Filter.eq(dto.getModelSpecificationKey()))
                .build();
        return modelSpecificationService.getOne(criteria, user)
                .map(ModelSpecification::getType)
                .map(modelProviderHubService::getProvider)
                .flatMapMany(modelProviderService -> modelProviderService.chat(dto, user));
    }
}
