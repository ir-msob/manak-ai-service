package ir.msob.manak.aiagent.ai;

import ir.msob.jima.core.commons.logger.Logger;
import ir.msob.jima.core.commons.logger.LoggerFactory;
import ir.msob.jima.core.commons.operation.OperationsStatus;
import ir.msob.manak.core.model.jima.security.User;
import ir.msob.manak.core.service.jima.security.UserService;
import ir.msob.manak.domain.model.aiagent.chat.ChatRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Mono;

import java.security.Principal;
import java.util.List;
import java.util.concurrent.ExecutionException;

@RestController
@RequestMapping(ChatRestResource.BASE_URI)
@RequiredArgsConstructor
public class ChatRestResource {
    public static final String BASE_URI = "/api/v1/ai";
    private static final Logger logger = LoggerFactory.getLogger(ChatRestResource.class);

    private final ChatService service;
    private final UserService userService;

    @PostMapping
    public Mono<ResponseEntity<List<String>>> chat(@RequestBody ChatRequest dto, Principal principal) throws ExecutionException, InterruptedException {
        logger.info("REST request to chat, dto : {}", dto);
        User user = userService.getUser(principal);
        return service.chat(dto, user).collectList().map(res -> ResponseEntity.status(OperationsStatus.SAVE).body(res));
    }

}
