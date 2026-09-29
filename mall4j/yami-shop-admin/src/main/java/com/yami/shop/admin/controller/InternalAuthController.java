package com.yami.shop.admin.controller;

import com.yami.shop.admin.vo.AiAuthContextVO;
import com.yami.shop.common.exception.YamiShopBindException;
import com.yami.shop.common.response.ResponseEnum;
import com.yami.shop.common.response.ServerResponseEntity;
import com.yami.shop.security.common.bo.UserInfoInTokenBO;
import com.yami.shop.security.common.util.AuthUserContext;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RestController;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

/**
 * 为内网 AI 服务提供商城用户 Token 鉴权结果。
 *
 * <p>请求会先经过商城现有 AuthFilter 校验 Authorization，再校验 AI 服务身份，
 * 最后返回脱敏后的用户上下文。该接口不返回商城 Token。</p>
 */
@RestController
@Tag(name = "内部鉴权")
@Slf4j
public class InternalAuthController {

    private static final String AI_SERVICE_TOKEN_HEADER = "X-Mall-Agent-Token";

    private final String aiServiceToken;

    public InternalAuthController(
            @Value("${ai.auth.service-token:}") String aiServiceToken) {
        this.aiServiceToken = aiServiceToken;
    }

    /**
     * 校验商城 Authorization，并返回当前用户的 AI 调用上下文。
     *
     * @param serviceToken Python AI 服务使用的内部服务 Token
     * @return 当前用户身份、租户和权限信息
     * @throws YamiShopBindException 用户 Token 或服务 Token 校验失败时抛出
     */
    @PostMapping("/internal/auth/introspect")
    @Operation(summary = "AI 服务内部鉴权", description = "校验商城 Token 并返回 AI 服务所需的用户上下文")
    public ServerResponseEntity<AiAuthContextVO> introspect(
            @RequestHeader(value = AI_SERVICE_TOKEN_HEADER, required = false) String serviceToken) {
        verifyAiService(serviceToken);

        UserInfoInTokenBO userInfo = AuthUserContext.get();
        if (userInfo == null || Boolean.FALSE.equals(userInfo.getEnabled())) {
            throw new YamiShopBindException(ResponseEnum.UNAUTHORIZED, "用户未通过鉴权");
        }

        AiAuthContextVO context = new AiAuthContextVO();
        context.setUserId(userInfo.getUserId());
        context.setShopId(userInfo.getShopId());
        context.setSysType(userInfo.getSysType());
        context.setIsAdmin(userInfo.getIsAdmin());
        context.setBizUserId(userInfo.getBizUserId());
        context.setPerms(userInfo.getPerms());
        context.setEnabled(userInfo.getEnabled());
        context.setOtherId(userInfo.getOtherId());

        log.info("AI鉴权成功");
        return ServerResponseEntity.success(context);
    }

    /**
     * 校验请求是否来自已配置的 Python AI 服务。
     *
     * @param serviceToken 请求头中的服务 Token
     * @throws YamiShopBindException 服务 Token 未配置或不匹配时抛出
     */
    private void verifyAiService(String serviceToken) {
        if (aiServiceToken == null || aiServiceToken.isBlank()
                || serviceToken == null || serviceToken.isBlank()) {
            throw new YamiShopBindException(ResponseEnum.UNAUTHORIZED, "AI 服务身份校验失败");
        }

        boolean matched = MessageDigest.isEqual(
                aiServiceToken.getBytes(StandardCharsets.UTF_8),
                serviceToken.getBytes(StandardCharsets.UTF_8));
        if (!matched) {
            throw new YamiShopBindException(ResponseEnum.UNAUTHORIZED, "AI 服务身份校验失败");
        }
    }
}
