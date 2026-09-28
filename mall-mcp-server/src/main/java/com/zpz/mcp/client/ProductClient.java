package com.zpz.mcp.client;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

/**
 * mall4j 商品、搜索、SKU 和评价 REST API 声明式客户端。
 */
@FeignClient(name = "mall4j-product", url = "${mall4j.base-url}")
public interface ProductClient {

    @GetMapping("/search/searchProdPage")
    String search(@RequestParam("prodName") String keyword,
                  @RequestParam("current") Integer current,
                  @RequestParam("size") Integer size,
                  @RequestParam("sort") Integer sort,
                  @RequestParam("orderBy") Integer orderBy,
                  @RequestParam("shopId") Long shopId);

    @GetMapping("/prod/prodInfo")
    String getDetail(@RequestParam("prodId") Long productId);

    @GetMapping("/sku/getSkuList")
    String getSkus(@RequestParam("prodId") Long productId);

    @GetMapping("/prod/lastedProdPage")
    String getNewest(@RequestParam("current") Integer current,
                     @RequestParam("size") Integer size);

    @GetMapping("/prod/moreBuyProdList")
    String getBestSellers(@RequestParam("current") Integer current,
                          @RequestParam("size") Integer size);

    @GetMapping("/prodComm/prodCommData")
    String getReviewSummary(@RequestParam("prodId") Long productId);

    @GetMapping("/prodComm/prodCommPageByProd")
    String getReviews(@RequestParam("prodId") Long productId,
                      @RequestParam(value = "evaluate", required = false) Integer evaluate,
                      @RequestParam("current") Integer current,
                      @RequestParam("size") Integer size);

    @GetMapping("/search/hotSearch")
    String getHotSearches(@RequestParam("number") Integer number,
                          @RequestParam("sort") Integer sort);
}
