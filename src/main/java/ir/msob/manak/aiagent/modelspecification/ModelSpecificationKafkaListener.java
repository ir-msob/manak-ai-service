package ir.msob.manak.aiagent.modelspecification;

import com.fasterxml.jackson.databind.ObjectMapper;
import ir.msob.jima.core.commons.client.BaseAsyncClient;
import ir.msob.jima.core.commons.operation.ConditionalOnOperation;
import ir.msob.jima.core.commons.resource.Resource;
import ir.msob.jima.core.commons.shared.ResourceType;
import ir.msob.jima.crud.api.kafka.client.ChannelUtil;
import ir.msob.manak.core.service.jima.crud.kafka.domain.service.DomainCrudKafkaListener;
import ir.msob.manak.core.service.jima.security.UserService;
import ir.msob.manak.domain.model.aiagent.modelspecification.ModelSpecification;
import ir.msob.manak.domain.model.aiagent.modelspecification.ModelSpecificationCriteria;
import ir.msob.manak.domain.model.aiagent.modelspecification.ModelSpecificationDto;
import ir.msob.manak.domain.model.aiagent.modelspecification.ModelSpecificationTypeReference;
import org.springframework.kafka.core.ConsumerFactory;
import org.springframework.stereotype.Component;

import static ir.msob.jima.core.commons.operation.Operations.*;

@Component
@ConditionalOnOperation(operations = {SAVE, UPDATE_BY_ID, DELETE_BY_ID})
@Resource(value = ModelSpecification.DOMAIN_NAME_WITH_HYPHEN, type = ResourceType.KAFKA)
public class ModelSpecificationKafkaListener
        extends DomainCrudKafkaListener<ModelSpecification, ModelSpecificationDto, ModelSpecificationCriteria, ModelSpecificationRepository, ModelSpecificationService>
        implements ModelSpecificationTypeReference {
    public static final String BASE_URI = ChannelUtil.getBaseChannel(ModelSpecificationDto.class);

    protected ModelSpecificationKafkaListener(UserService userService, ModelSpecificationService service, ObjectMapper objectMapper, ConsumerFactory<String, String> consumerFactory, BaseAsyncClient asyncClient) {
        super(userService, service, objectMapper, consumerFactory, asyncClient);
    }

}
