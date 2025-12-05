package ir.msob.manak.ai.summarizer;

import ir.msob.jima.core.commons.logger.Logger;
import ir.msob.jima.core.commons.logger.LoggerFactory;
import ir.msob.manak.core.model.jima.security.User;
import ir.msob.manak.core.service.jima.security.UserService;
import ir.msob.manak.domain.model.ai.summarizer.SummarizerRequestDto;
import ir.msob.manak.domain.model.ai.summarizer.SummarizerResponseDto;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Mono;

import java.security.Principal;

@RestController
@RequestMapping(SummarizerRestResource.BASE_URI)
@RequiredArgsConstructor
public class SummarizerRestResource {
    public static final String BASE_URI = "/api/v1/" + SummarizerRequestDto.DOMAIN_NAME_WITH_HYPHEN;
    private static final Logger logger = LoggerFactory.getLogger(SummarizerRestResource.class);

    private final SummarizerService service;
    private final UserService userService;

    @PostMapping
    public ResponseEntity<Mono<SummarizerResponseDto>> summarize(@RequestBody SummarizerRequestDto dto, Principal principal) {
        logger.info("REST request to embedding, dto : {}", dto);
        User user = userService.getUser(principal);
        Mono<SummarizerResponseDto> res = service.summarize(dto, user);
        return ResponseEntity.ok(res);
    }

}
