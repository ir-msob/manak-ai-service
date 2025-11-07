package ir.msob.manak.chat.modelspecification;

import com.fasterxml.jackson.databind.ObjectMapper;
import ir.msob.jima.core.commons.id.BaseIdService;
import ir.msob.jima.core.commons.operation.BaseBeforeAfterDomainOperation;
import ir.msob.jima.crud.service.domain.BeforeAfterComponent;
import ir.msob.manak.core.model.jima.security.User;
import ir.msob.manak.core.service.jima.crud.base.childdomain.ChildDomainCrudService;
import ir.msob.manak.core.service.jima.crud.base.domain.DomainCrudService;
import ir.msob.manak.core.service.jima.service.IdService;
import ir.msob.manak.domain.model.chat.modelspecification.ModelSpecification;
import ir.msob.manak.domain.model.chat.modelspecification.ModelSpecificationCriteria;
import ir.msob.manak.domain.model.chat.modelspecification.ModelSpecificationDto;
import jakarta.validation.Valid;
import org.modelmapper.ModelMapper;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import reactor.core.publisher.Mono;

import java.util.Collection;
import java.util.Collections;

@Service
public class ModelSpecificationService extends DomainCrudService<ModelSpecification, ModelSpecificationDto, ModelSpecificationCriteria, ModelSpecificationRepository>
        implements ChildDomainCrudService<ModelSpecificationDto> {

    private final ModelMapper modelMapper;
    private final IdService idService;

    protected ModelSpecificationService(BeforeAfterComponent beforeAfterComponent, ObjectMapper objectMapper, ModelSpecificationRepository repository, ModelMapper modelMapper, IdService idService) {
        super(beforeAfterComponent, objectMapper, repository);
        this.modelMapper = modelMapper;
        this.idService = idService;
    }

    @Override
    public ModelSpecificationDto toDto(ModelSpecification domain, User user) {
        return modelMapper.map(domain, ModelSpecificationDto.class);
    }

    @Override
    public ModelSpecification toDomain(ModelSpecificationDto dto, User user) {
        return dto;
    }

    @Override
    public Collection<BaseBeforeAfterDomainOperation<String, User, ModelSpecificationDto, ModelSpecificationCriteria>> getBeforeAfterDomainOperations() {
        return Collections.emptyList();
    }

    @Transactional
    @Override
    public Mono<ModelSpecificationDto> getDto(String id, User user) {
        return super.getOne(id, user);
    }

    @Transactional
    @Override
    public Mono<ModelSpecificationDto> updateDto(String id, @Valid ModelSpecificationDto dto, User user) {
        return super.update(id, dto, user);
    }

    @Override
    public BaseIdService getIdService() {
        return idService;
    }
}
