package com.yami.shop.admin.vo;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

import java.util.Set;

/**
 * AI 服务调用商城内部鉴权接口时使用的用户上下文。
 *
 * <p>该对象只返回当前用户的身份、租户和权限信息，不包含商城访问 Token。</p>
 */
@Data
@Schema(name = "AiAuthContextVO", description = "AI 服务使用的商城用户鉴权上下文")
public class AiAuthContextVO {

    /** 用户在商城系统中的用户 ID。 */
    @Schema(description = "用户 ID")
    private String userId;

    /** 店铺或租户 ID。 */
    @Schema(description = "店铺 ID")
    private Long shopId;

    /** 系统类型，取值对应 SysTypeEnum。 */
    @Schema(description = "系统类型")
    private Integer sysType;

    /** 是否为管理员。 */
    @Schema(description = "是否为管理员")
    private Integer isAdmin;

    /** 业务用户 ID。 */
    @Schema(description = "业务用户 ID")
    private String bizUserId;

    /** 当前用户权限集合。 */
    @Schema(description = "权限集合")
    private Set<String> perms;

    /** 当前用户是否启用。 */
    @Schema(description = "用户是否启用")
    private Boolean enabled;

    /** 关联的其他业务 ID。 */
    @Schema(description = "其他业务 ID")
    private Long otherId;
}
