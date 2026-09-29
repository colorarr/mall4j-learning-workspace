package com.yami.shop.api.controller.ai;


import com.yami.shop.common.response.ServerResponseEntity;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/p/agent")
@Slf4j
public class AIChatController {


    @GetMapping("/chat")
    public ServerResponseEntity chat(String messages){
        return ServerResponseEntity.success(messages);
    }

}
