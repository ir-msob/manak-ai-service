package ir.msob.manak.ai.modelspecification;

import ir.msob.jima.core.commons.resource.BaseResource;
import ir.msob.jima.core.test.CoreTestData;
import ir.msob.manak.ai.Application;
import ir.msob.manak.ai.ContainerConfiguration;
import ir.msob.manak.core.model.jima.security.User;
import ir.msob.manak.core.test.jima.crud.kafka.domain.DomainCrudKafkaListenerTest;
import ir.msob.manak.domain.model.ai.modelspecification.ModelSpecification;
import ir.msob.manak.domain.model.ai.modelspecification.ModelSpecificationCriteria;
import ir.msob.manak.domain.model.ai.modelspecification.ModelSpecificationDto;
import ir.msob.manak.domain.model.ai.modelspecification.ModelSpecificationTypeReference;
import lombok.SneakyThrows;
import lombok.extern.apachecommons.CommonsLog;
import org.bson.types.ObjectId;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.springframework.boot.test.context.SpringBootTest;
import org.testcontainers.junit.jupiter.Testcontainers;

@SpringBootTest(classes = {Application.class, ContainerConfiguration.class}, webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
@CommonsLog
class ModelSpecificationKafkaListenerIT
        extends DomainCrudKafkaListenerTest<ModelSpecification, ModelSpecificationDto, ModelSpecificationCriteria, ModelSpecificationRepository, ModelSpecificationService, ModelSpecificationDataProvider>
        implements ModelSpecificationTypeReference {

    @SneakyThrows
    @BeforeAll
    static void beforeAll() {
        CoreTestData.init(new ObjectId(), new ObjectId());
    }

    @SneakyThrows
    @BeforeEach
    void beforeEach() {
        getDataProvider().cleanups();
        ModelSpecificationDataProvider.createMandatoryNewDto();
        ModelSpecificationDataProvider.createNewDto();
    }

    @Override
    public Class<? extends BaseResource<String, User>> getResourceClass() {
        return ModelSpecificationKafkaListener.class;
    }

    @Override
    public String getBaseUri() {
        return ModelSpecificationKafkaListener.BASE_URI;
    }
}
