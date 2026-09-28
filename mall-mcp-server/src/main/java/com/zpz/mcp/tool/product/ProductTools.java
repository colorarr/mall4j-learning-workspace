package com.zpz.mcp.tool.product;

import com.zpz.mcp.client.Mall4jClientExecutor;
import com.zpz.mcp.client.ProductClient;
import jakarta.annotation.Resource;
import org.springframework.ai.mcp.annotation.McpTool;
import org.springframework.ai.mcp.annotation.McpToolParam;
import org.springframework.stereotype.Component;


/**
 * 将商品查询和导购 MCP 工具转发到 mall4j REST API。
 */
@Component
public class ProductTools {

    private static final int DEFAULT_PAGE = 1;
    private static final int DEFAULT_SIZE = 10;
    private static final int MAX_SIZE = 20;

    @Resource
    private ProductClient productClient;

    @Resource
    private Mall4jClientExecutor clientExecutor;

    /**
     * 根据关键词分页搜索商品。
     *
     * @return mall4j 商品搜索响应
     */
    @McpTool(
            name = "product_search",
            title = "搜索商品",
            description = "根据商品关键词分页搜索商品。sort取0默认、1销量、2价格；orderBy取0升序、1降序。",
            annotations = @McpTool.McpAnnotations(
                    title = "搜索商品",
                    readOnlyHint = true,
                    destructiveHint = false,
                    idempotentHint = true,
                    openWorldHint = false
            )
    )
    public String search(
            @McpToolParam(description = "商品名称或搜索关键词", required = true) String keyword,
            @McpToolParam(description = "页码，默认1", required = false) Integer current,
            @McpToolParam(description = "每页数量，默认10，最大20", required = false) Integer size,
            @McpToolParam(description = "排序类型：0默认、1销量、2价格", required = false) Integer sort,
            @McpToolParam(description = "排序方向：0升序、1降序", required = false) Integer orderBy,
            @McpToolParam(description = "店铺ID，全平台搜索时传0", required = false) Long shopId) {
        return clientExecutor.execute(
                "product_search",
                () -> productClient.search(
                        keyword,
                        normalizeCurrent(current),
                        normalizeSize(size),
                        sort == null ? 0 : sort,
                        orderBy == null ? 0 : orderBy,
                        shopId == null ? 0L : shopId
                )
        );
    }

    /**
     * 查询商品详情。
     *
     * @param productId 商品 ID
     * @return mall4j 商品详情响应
     */
    @McpTool(
            name = "product_get_detail",
            title = "查询商品详情",
            description = "根据商品ID查询商品详情、可用SKU、价格、库存和配送信息。",
            annotations = @McpTool.McpAnnotations(
                    title = "查询商品详情",
                    readOnlyHint = true,
                    destructiveHint = false,
                    idempotentHint = true,
                    openWorldHint = false
            )
    )
    public String getDetail(
            @McpToolParam(description = "商品ID", required = true) Long productId) {
        return clientExecutor.execute("product_get_detail", () -> productClient.getDetail(productId));
    }

    /**
     * 查询商品的 SKU 规格列表。
     *
     * @param productId 商品 ID
     * @return mall4j SKU 响应
     */
    @McpTool(
            name = "product_get_skus",
            title = "查询商品规格",
            description = "根据商品ID查询全部可选SKU规格、价格和库存。",
            annotations = @McpTool.McpAnnotations(
                    title = "查询商品规格",
                    readOnlyHint = true,
                    destructiveHint = false,
                    idempotentHint = true,
                    openWorldHint = false
            )
    )
    public String getSkus(
            @McpToolParam(description = "商品ID", required = true) Long productId) {
        return clientExecutor.execute("product_get_skus", () -> productClient.getSkus(productId));
    }

    /**
     * 查询新品推荐列表。
     *
     * @return mall4j 商品分页响应
     */
    @McpTool(
            name = "product_get_newest",
            title = "查询新品推荐",
            description = "分页查询商城最新上架的商品，可用于没有明确关键词时的新品推荐。",
            annotations = @McpTool.McpAnnotations(
                    title = "查询新品推荐",
                    readOnlyHint = true,
                    destructiveHint = false,
                    idempotentHint = true,
                    openWorldHint = false
            )
    )
    public String getNewest(
            @McpToolParam(description = "页码，默认1", required = false) Integer current,
            @McpToolParam(description = "每页数量，默认10，最大20", required = false) Integer size) {
        return clientExecutor.execute(
                "product_get_newest",
                () -> productClient.getNewest(normalizeCurrent(current), normalizeSize(size))
        );
    }

    /**
     * 查询热销商品列表。
     *
     * @return mall4j 商品分页响应
     */
    @McpTool(
            name = "product_get_best_sellers",
            title = "查询热销商品",
            description = "分页查询商城销量较高的商品，可用于热门商品推荐。",
            annotations = @McpTool.McpAnnotations(
                    title = "查询热销商品",
                    readOnlyHint = true,
                    destructiveHint = false,
                    idempotentHint = true,
                    openWorldHint = false
            )
    )
    public String getBestSellers(
            @McpToolParam(description = "页码，默认1", required = false) Integer current,
            @McpToolParam(description = "每页数量，默认10，最大20", required = false) Integer size) {
        return clientExecutor.execute(
                "product_get_best_sellers",
                () -> productClient.getBestSellers(normalizeCurrent(current), normalizeSize(size))
        );
    }

    /**
     * 查询商品评论汇总。
     *
     * @param productId 商品 ID
     * @return mall4j 评论汇总响应
     */
    @McpTool(
            name = "product_get_review_summary",
            title = "查询商品评价汇总",
            description = "查询指定商品的好评率以及好评、中评、差评数量。",
            annotations = @McpTool.McpAnnotations(
                    title = "查询商品评价汇总",
                    readOnlyHint = true,
                    destructiveHint = false,
                    idempotentHint = true,
                    openWorldHint = false
            )
    )
    public String getReviewSummary(
            @McpToolParam(description = "商品ID", required = true) Long productId) {
        return clientExecutor.execute(
                "product_get_review_summary",
                () -> productClient.getReviewSummary(productId)
        );
    }

    /**
     * 分页查询商品评论。
     *
     * @return mall4j 评论分页响应
     */
    @McpTool(
            name = "product_get_reviews",
            title = "查询商品评价",
            description = "分页查询指定商品的评价；evaluate可用于筛选评价等级，未指定时查询全部。",
            annotations = @McpTool.McpAnnotations(
                    title = "查询商品评价",
                    readOnlyHint = true,
                    destructiveHint = false,
                    idempotentHint = true,
                    openWorldHint = false
            )
    )
    public String getReviews(
            @McpToolParam(description = "商品ID", required = true) Long productId,
            @McpToolParam(description = "评价等级筛选，未指定时查询全部", required = false) Integer evaluate,
            @McpToolParam(description = "页码，默认1", required = false) Integer current,
            @McpToolParam(description = "每页数量，默认10，最大20", required = false) Integer size) {
        return clientExecutor.execute(
                "product_get_reviews",
                () -> productClient.getReviews(
                        productId,
                        evaluate,
                        normalizeCurrent(current),
                        normalizeSize(size)
                )
        );
    }

    /**
     * 查询全局热搜词。
     *
     * @return mall4j 热搜响应
     */
    @McpTool(
            name = "product_get_hot_searches",
            title = "查询热门搜索",
            description = "查询商城热门搜索词，可用于用户没有明确购物目标时提供搜索方向。",
            annotations = @McpTool.McpAnnotations(
                    title = "查询热门搜索",
                    readOnlyHint = true,
                    destructiveHint = false,
                    idempotentHint = false,
                    openWorldHint = false
            )
    )
    public String getHotSearches(
            @McpToolParam(description = "返回热搜数量，默认10，最大20", required = false) Integer number,
            @McpToolParam(description = "是否按配置顺序返回：0随机、1按顺序", required = false) Integer sort) {
        int actualNumber = number == null ? DEFAULT_SIZE : Math.max(1, Math.min(number, MAX_SIZE));
        return clientExecutor.execute(
                "product_get_hot_searches",
                () -> productClient.getHotSearches(actualNumber, sort == null ? 1 : sort)
        );
    }

    private int normalizeCurrent(Integer current) {
        return current == null ? DEFAULT_PAGE : Math.max(1, current);
    }

    private int normalizeSize(Integer size) {
        return size == null ? DEFAULT_SIZE : Math.max(1, Math.min(size, MAX_SIZE));
    }
}
