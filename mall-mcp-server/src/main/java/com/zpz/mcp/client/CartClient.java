package com.zpz.mcp.client;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.http.HttpHeaders;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;

import java.util.List;
import java.util.Map;

/**
 * mall4j 用户购物车 REST API 声明式客户端。
 */
@FeignClient(name = "mall4j-cart", url = "${mall4j.base-url}")
public interface CartClient {

    @PostMapping("/p/shopCart/info")
    String getCart(@RequestHeader(HttpHeaders.AUTHORIZATION) String authorization,
                   @RequestBody Map<String, Object> selections);

    @PostMapping("/p/shopCart/changeItem")
    String changeItem(@RequestHeader(HttpHeaders.AUTHORIZATION) String authorization,
                      @RequestBody Map<String, Object> request);

    @DeleteMapping("/p/shopCart/deleteItem")
    String removeItems(@RequestHeader(HttpHeaders.AUTHORIZATION) String authorization,
                       @RequestBody List<Long> basketIds);

    @DeleteMapping("/p/shopCart/deleteAll")
    String clear(@RequestHeader(HttpHeaders.AUTHORIZATION) String authorization);

    @GetMapping("/p/shopCart/prodCount")
    String getCount(@RequestHeader(HttpHeaders.AUTHORIZATION) String authorization);

    @PostMapping("/p/shopCart/totalPay")
    String getTotal(@RequestHeader(HttpHeaders.AUTHORIZATION) String authorization,
                    @RequestBody List<Long> basketIds);

    @GetMapping("/p/shopCart/expiryProdList")
    String getExpiredItems(@RequestHeader(HttpHeaders.AUTHORIZATION) String authorization);

    @DeleteMapping("/p/shopCart/cleanExpiryProdList")
    String cleanExpiredItems(@RequestHeader(HttpHeaders.AUTHORIZATION) String authorization);
}
