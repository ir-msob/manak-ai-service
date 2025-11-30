package ir.msob.manak.ai.modelspecification;

import ir.msob.jima.core.ral.mongo.commons.query.MongoQueryBuilder;
import ir.msob.manak.core.service.jima.crud.base.domain.DomainCrudRepository;
import ir.msob.manak.domain.model.chat.modelspecification.ModelSpecification;
import org.springframework.data.mongodb.core.ReactiveMongoTemplate;
import org.springframework.stereotype.Repository;

@Repository
public class ModelSpecificationRepository extends DomainCrudRepository<ModelSpecification> {
    protected ModelSpecificationRepository(MongoQueryBuilder queryBuilder, ReactiveMongoTemplate reactiveMongoTemplate) {
        super(queryBuilder, reactiveMongoTemplate);
    }
}

