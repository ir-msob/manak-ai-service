package ir.msob.manak.ai.modelspecification;

import ir.msob.jima.core.commons.resource.BaseResource;
import ir.msob.jima.core.test.CoreTestData;
import ir.msob.manak.ai.Application;
import ir.msob.manak.ai.ContainerConfiguration;
import ir.msob.manak.core.model.jima.security.User;
import ir.msob.manak.core.test.jima.crud.restful.domain.DomainCrudRestResourceTest;
import ir.msob.manak.domain.model.chat.modelspecification.ModelSpecification;
import ir.msob.manak.domain.model.chat.modelspecification.ModelSpecificationCriteria;
import ir.msob.manak.domain.model.chat.modelspecification.ModelSpecificationDto;
import ir.msob.manak.domain.model.chat.modelspecification.ModelSpecificationTypeReference;
import lombok.SneakyThrows;
import lombok.extern.apachecommons.CommonsLog;
import org.bson.types.ObjectId;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.springframework.boot.test.autoconfigure.web.reactive.AutoConfigureWebTestClient;
import org.springframework.boot.test.context.SpringBootTest;
import org.testcontainers.junit.jupiter.Testcontainers;

@AutoConfigureWebTestClient
@SpringBootTest(classes = {Application.class, ContainerConfiguration.class}, webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
@CommonsLog
class ModelSpecificationRestResourceIT
        extends DomainCrudRestResourceTest<ModelSpecification, ModelSpecificationDto, ModelSpecificationCriteria, ModelSpecificationRepository, ModelSpecificationService, ModelSpecificationDataProvider>
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
    public String getBaseUri() {
        return ModelSpecificationRestResource.BASE_URI;
    }

    @Override
    public Class<? extends BaseResource<String, User>> getResourceClass() {
        return ModelSpecificationRestResource.class;
    }

}
