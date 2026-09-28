package com.zpz.mcp.tool.address;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

/**
 * 新增或修改收货地址的请求。
 *
 * @param addressId 地址 ID，新增时为空，修改时必填
 * @param receiver 收货人
 * @param detailAddress 详细地址
 * @param postCode 邮编
 * @param mobile 手机号
 * @param provinceId 省 ID
 * @param cityId 市 ID
 * @param areaId 区县 ID
 * @param province 省名称
 * @param city 市名称
 * @param area 区县名称
 */
public record AddressRequest(
        Long addressId,
        @NotBlank String receiver,
        @NotBlank String detailAddress,
        String postCode,
        @NotBlank String mobile,
        @NotNull Long provinceId,
        @NotNull Long cityId,
        @NotNull Long areaId,
        @NotBlank String province,
        @NotBlank String city,
        @NotBlank String area
) {
}
