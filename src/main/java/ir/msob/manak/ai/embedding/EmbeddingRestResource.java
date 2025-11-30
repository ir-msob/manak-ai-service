package ir.msob.manak.ai.embedding;

import ir.msob.jima.core.commons.logger.Logger;
import ir.msob.jima.core.commons.logger.LoggerFactory;
import ir.msob.manak.core.model.jima.security.User;
import ir.msob.manak.core.service.jima.security.UserService;
import ir.msob.manak.domain.model.chat.embedding.EmbeddingRequestDto;
import ir.msob.manak.domain.model.chat.embedding.EmbeddingResponseDto;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Mono;

import java.security.Principal;

@RestController
@RequestMapping(EmbeddingRestResource.BASE_URI)
@RequiredArgsConstructor
public class EmbeddingRestResource {
    public static final String BASE_URI = "/api/v1/" + EmbeddingRequestDto.DOMAIN_NAME_WITH_HYPHEN;
    private static final Logger logger = LoggerFactory.getLogger(EmbeddingRestResource.class);

    private final EmbeddingService service;
    private final UserService userService;

    @PostMapping
    public ResponseEntity<Mono<EmbeddingResponseDto>> embedding(@RequestBody EmbeddingRequestDto dto, Principal principal) {
        logger.info("REST request to embedding, dto : {}", dto);
        User user = userService.getUser(principal);
        Mono<EmbeddingResponseDto> res = service.embedding(dto, user);
        return ResponseEntity.ok(res);
    }

}
