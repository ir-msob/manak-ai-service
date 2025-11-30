package ir.msob.manak.ai.model;

import com.fasterxml.jackson.annotation.JsonInclude;
import ir.msob.manak.domain.model.chat.modelspecification.ModelSpecification;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import lombok.*;

import java.util.ArrayList;
import java.util.List;

@Setter
@Getter
@ToString(callSuper = true)
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ModelEntry<T> {
    @NotEmpty
    private String key;
    @NotEmpty
    @Singular
    private List<ModelSpecification.ModelType> modelTypes = new ArrayList<>();
    @NotNull
    private T model;
}
