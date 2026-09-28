package com.zpz.mcp.tool.cart;

import jakarta.validation.constraints.NotNull;

/**
 * 添加或调整购物车商品数量的请求。
 *
 * @param basketId 购物车明细 ID，新增商品时可以为空
 * @param productId 商品 ID
 * @param skuId SKU ID
 * @param shopId 店铺 ID
 * @param changeCount 数量变化值，正数增加、负数减少
 * @param distributionCardNo 分销推广卡号，没有时为空
 */
public record CartChangeRequest(
        Long basketId,
        @NotNull Long productId,
        @NotNull Long skuId,
        @NotNull Long shopId,
        @NotNull Integer changeCount,
        String distributionCardNo
) {
}
