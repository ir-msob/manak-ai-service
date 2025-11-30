package ir.msob.manak.ai.modelspecification;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.github.fge.jackson.jsonpointer.JsonPointerException;
import com.github.fge.jsonpatch.JsonPatch;
import com.github.fge.jsonpatch.JsonPatchOperation;
import ir.msob.jima.core.commons.id.BaseIdService;
import ir.msob.manak.core.test.jima.crud.base.domain.DomainCrudDataProvider;
import ir.msob.manak.domain.model.chat.modelspecification.ModelSpecification;
import ir.msob.manak.domain.model.chat.modelspecification.ModelSpecificationCriteria;
import ir.msob.manak.domain.model.chat.modelspecification.ModelSpecificationDto;
import lombok.SneakyThrows;
import org.assertj.core.api.Assertions;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;

import static ir.msob.jima.core.test.CoreTestData.DEFAULT_STRING;
import static ir.msob.jima.core.test.CoreTestData.UPDATED_STRING;

/**
 * This class provides test data for the {@link ModelSpecification} class. It extends the {@link DomainCrudDataProvider} class
 * and provides methods to create new test data objects, update existing data objects, and generate JSON patches for updates.
 */
@Component
public class ModelSpecificationDataProvider extends DomainCrudDataProvider<ModelSpecification, ModelSpecificationDto, ModelSpecificationCriteria, ModelSpecificationRepository, ModelSpecificationService> {

    private static ModelSpecificationDto newDto;
    private static ModelSpecificationDto newMandatoryDto;

    protected ModelSpecificationDataProvider(BaseIdService idService, ObjectMapper objectMapper, ModelSpecificationService service) {
        super(idService, objectMapper, service);
    }

    /**
     * Creates a new DTO object with default values.
     */
    public static void createNewDto() {
        newDto = prepareMandatoryDto();
        newDto.setDescription(DEFAULT_STRING);
    }

    /**
     * Creates a new DTO object with mandatory fields set.
     */
    public static void createMandatoryNewDto() {
        newMandatoryDto = prepareMandatoryDto();
    }

    /**
     * Creates a new DTO object with mandatory fields set.
     */
    public static ModelSpecificationDto prepareMandatoryDto() {
        ModelSpecificationDto dto = new ModelSpecificationDto();
        dto.setName(DEFAULT_STRING);
        return dto;
    }

    /**
     */
    @Override
    @SneakyThrows
    public JsonPatch getJsonPatch() {
        List<JsonPatchOperation> operations = getMandatoryJsonPatchOperation();
        return new JsonPatch(operations);
    }

    /**
     */
    @Override
    @SneakyThrows
    public JsonPatch getMandatoryJsonPatch() {
        return new JsonPatch(getMandatoryJsonPatchOperation());
    }

    /**
     *
     */
    @Override
    public ModelSpecificationDto getNewDto() {
        return newDto;
    }

    /**
     * Updates the given DTO object with the updated value for the domain field.
     *
     * @param dto the DTO object to update
     */
    @Override
    public void updateDto(ModelSpecificationDto dto) {
        updateMandatoryDto(dto);
        dto.setDescription(UPDATED_STRING);
    }

    /**
     *
     */
    @Override
    public ModelSpecificationDto getMandatoryNewDto() {
        return newMandatoryDto;
    }

    /**
     * Updates the given DTO object with the updated value for the mandatory field.
     *
     * @param dto the DTO object to update
     */
    @Override
    public void updateMandatoryDto(ModelSpecificationDto dto) {
        dto.setName(UPDATED_STRING);
    }

    /**
     * Creates a list of JSON patch operations for updating the mandatory field.
     *
     * @return a list of JSON patch operations
     * @throws JsonPointerException if there is an error creating the JSON pointer.
     */
    public List<JsonPatchOperation> getMandatoryJsonPatchOperation() throws JsonPointerException {
        return new ArrayList<>();
    }

    @Override
    public void assertMandatoryGet(ModelSpecificationDto before, ModelSpecificationDto after) {
        super.assertMandatoryGet(before, after);
        Assertions.assertThat(after.getName()).isEqualTo(before.getName());
    }

    @Override
    public void assertGet(ModelSpecificationDto before, ModelSpecificationDto after) {
        super.assertGet(before, after);
        assertMandatoryGet(before, after);

        Assertions.assertThat(after.getDescription()).isEqualTo(before.getDescription());
    }

    @Override
    public void assertMandatoryUpdate(ModelSpecificationDto dto, ModelSpecificationDto updatedDto) {
        super.assertMandatoryUpdate(dto, updatedDto);
        Assertions.assertThat(dto.getName()).isEqualTo(DEFAULT_STRING);
        Assertions.assertThat(updatedDto.getName()).isEqualTo(UPDATED_STRING);
    }

    @Override
    public void assertUpdate(ModelSpecificationDto dto, ModelSpecificationDto updatedDto) {
        super.assertUpdate(dto, updatedDto);
        assertMandatoryUpdate(dto, updatedDto);
    }

    @Override
    public void assertMandatorySave(ModelSpecificationDto dto, ModelSpecificationDto savedDto) {
        super.assertMandatorySave(dto, savedDto);
        assertMandatoryGet(dto, savedDto);
    }

    @Override
    public void assertSave(ModelSpecificationDto dto, ModelSpecificationDto savedDto) {
        super.assertSave(dto, savedDto);
        assertGet(dto, savedDto);
    }
}