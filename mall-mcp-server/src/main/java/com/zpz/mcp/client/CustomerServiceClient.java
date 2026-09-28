package com.zpz.mcp.client;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestParam;

/**
 * mall4j 商城公告 REST API 声明式客户端。
 */
@FeignClient(name = "mall4j-customer-service", url = "${mall4j.base-url}")
public interface CustomerServiceClient {

    @GetMapping("/shop/notice/topNoticeList")
    String getTopNotices();

    @GetMapping("/shop/notice/noticeList")
    String listNotices(@RequestParam("current") Integer current,
                       @RequestParam("size") Integer size);

    @GetMapping("/shop/notice/info/{noticeId}")
    String getNoticeDetail(@PathVariable("noticeId") Long noticeId);
}
