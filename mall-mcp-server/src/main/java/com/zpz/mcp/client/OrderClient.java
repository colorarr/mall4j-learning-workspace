package com.zpz.mcp.client;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.http.HttpHeaders;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestParam;

/**
 * mall4j 用户订单与物流 REST API 声明式客户端。
 */
@FeignClient(name = "mall4j-order", url = "${mall4j.base-url}")
public interface OrderClient {

    @GetMapping("/p/myOrder/myOrder")
    String list(@RequestHeader(HttpHeaders.AUTHORIZATION) String authorization,
                @RequestParam("status") Integer status,
                @RequestParam("current") Integer current,
                @RequestParam("size") Integer size);

    @GetMapping("/p/myOrder/orderDetail")
    String getDetail(@RequestHeader(HttpHeaders.AUTHORIZATION) String authorization,
                     @RequestParam("orderNumber") String orderNumber);

    @GetMapping("/p/myOrder/orderCount")
    String getCounts(@RequestHeader(HttpHeaders.AUTHORIZATION) String authorization);

    @GetMapping("/delivery/check")
    String getLogistics(@RequestHeader(HttpHeaders.AUTHORIZATION) String authorization,
                        @RequestParam("orderNumber") String orderNumber);

    @PutMapping("/p/myOrder/cancel/{orderNumber}")
    String cancel(@RequestHeader(HttpHeaders.AUTHORIZATION) String authorization,
                  @PathVariable("orderNumber") String orderNumber);

    @PutMapping("/p/myOrder/receipt/{orderNumber}")
    String confirmReceipt(@RequestHeader(HttpHeaders.AUTHORIZATION) String authorization,
                          @PathVariable("orderNumber") String orderNumber);

    @DeleteMapping("/p/myOrder/{orderNumber}")
    String deleteHistory(@RequestHeader(HttpHeaders.AUTHORIZATION) String authorization,
                         @PathVariable("orderNumber") String orderNumber);
}
