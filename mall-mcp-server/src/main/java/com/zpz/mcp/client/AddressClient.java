package com.zpz.mcp.client;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.http.HttpHeaders;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;

import java.util.Map;

/**
 * mall4j 用户收货地址 REST API 声明式客户端。
 */
@FeignClient(name = "mall4j-address", url = "${mall4j.base-url}")
public interface AddressClient {

    @GetMapping("/p/address/list")
    String list(@RequestHeader(HttpHeaders.AUTHORIZATION) String authorization);

    @GetMapping("/p/address/addrInfo/{addressId}")
    String getDetail(@RequestHeader(HttpHeaders.AUTHORIZATION) String authorization,
                     @PathVariable("addressId") Long addressId);

    @PostMapping("/p/address/addAddr")
    String add(@RequestHeader(HttpHeaders.AUTHORIZATION) String authorization,
               @RequestBody Map<String, Object> request);

    @PutMapping("/p/address/updateAddr")
    String update(@RequestHeader(HttpHeaders.AUTHORIZATION) String authorization,
                  @RequestBody Map<String, Object> request);

    @DeleteMapping("/p/address/deleteAddr/{addressId}")
    String delete(@RequestHeader(HttpHeaders.AUTHORIZATION) String authorization,
                  @PathVariable("addressId") Long addressId);

    @PutMapping("/p/address/defaultAddr/{addressId}")
    String setDefault(@RequestHeader(HttpHeaders.AUTHORIZATION) String authorization,
                      @PathVariable("addressId") Long addressId);
}
