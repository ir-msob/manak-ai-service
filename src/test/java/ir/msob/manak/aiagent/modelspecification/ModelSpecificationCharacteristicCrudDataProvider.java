package ir.msob.manak.aiagent.modelspecification;

import ir.msob.manak.core.test.jima.crud.base.childdomain.characteristic.BaseCharacteristicCrudDataProvider;
import ir.msob.manak.domain.model.aiagent.modelspecification.ModelSpecificationDto;
import org.springframework.stereotype.Component;

@Component
public class ModelSpecificationCharacteristicCrudDataProvider extends BaseCharacteristicCrudDataProvider<ModelSpecificationDto, ModelSpecificationService> {
    public ModelSpecificationCharacteristicCrudDataProvider(ModelSpecificationService childService) {
        super(childService);
    }
}
