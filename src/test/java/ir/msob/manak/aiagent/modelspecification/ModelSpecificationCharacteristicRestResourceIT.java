package ir.msob.manak.aiagent.modelspecification;

import ir.msob.jima.core.commons.resource.BaseResource;
import ir.msob.jima.core.test.CoreTestData;
import ir.msob.manak.aiagent.Application;
import ir.msob.manak.aiagent.ContainerConfiguration;
import ir.msob.manak.core.model.jima.security.User;
import ir.msob.manak.core.test.jima.crud.restful.childdomain.BaseCharacteristicCrudRestResourceTest;
import ir.msob.manak.domain.model.aiagent.modelspecification.ModelSpecification;
import ir.msob.manak.domain.model.aiagent.modelspecification.ModelSpecificationCriteria;
import ir.msob.manak.domain.model.aiagent.modelspecification.ModelSpecificationDto;
import ir.msob.manak.domain.model.aiagent.modelspecification.ModelSpecificationTypeReference;
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
public class ModelSpecificationCharacteristicRestResourceIT
        extends BaseCharacteristicCrudRestResourceTest<ModelSpecification, ModelSpecificationDto, ModelSpecificationCriteria, ModelSpecificationRepository, ModelSpecificationService, ModelSpecificationDataProvider, ModelSpecificationService, ModelSpecificationCharacteristicCrudDataProvider>
        implements ModelSpecificationTypeReference {

    @SneakyThrows
    @BeforeAll
    public static void beforeAll() {
        CoreTestData.init(new ObjectId(), new ObjectId());
    }

    @SneakyThrows
    @BeforeEach
    public void beforeEach() {
        getDataProvider().cleanups();
        ModelSpecificationDataProvider.createMandatoryNewDto();
        ModelSpecificationDataProvider.createNewDto();
        ModelSpecificationCharacteristicCrudDataProvider.createNewChild();
    }


    @Override
    public String getBaseUri() {
        return ModelSpecificationRestResource.BASE_URI;
    }

    @Override
    public Class<? extends BaseResource<String, User>> getResourceClass() {
        return ModelSpecificationCharacteristicRestResource.class;
    }
}
