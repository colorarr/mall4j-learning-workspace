package com.zpz.mcp.tool.address;

import com.zpz.mcp.client.AddressClient;
import com.zpz.mcp.client.Mall4jClientExecutor;
import com.zpz.mcp.support.McpAuthorization;
import jakarta.annotation.Resource;
import org.springframework.ai.mcp.annotation.McpTool;
import org.springframework.ai.mcp.annotation.McpToolParam;
import org.springframework.ai.mcp.annotation.context.McpSyncRequestContext;
import org.springframework.stereotype.Component;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 将收货地址 MCP 工具转发到 mall4j 地址 REST API。
 */
@Component
public class AddressTools {

    @Resource
    private AddressClient addressClient;

    @Resource
    private Mall4jClientExecutor clientExecutor;

    /**
     * 查询当前用户全部收货地址。
     */
    @McpTool(
            name = "address_list",
            title = "查询收货地址",
            description = "查询当前登录用户的全部收货地址，默认地址排在前面。",
            annotations = @McpTool.McpAnnotations(
                    title = "查询收货地址",
                    readOnlyHint = true,
                    destructiveHint = false,
                    idempotentHint = true,
                    openWorldHint = false
            )
    )
    public String list(McpSyncRequestContext context) {
        String authorization = McpAuthorization.required(context);
        return clientExecutor.execute("address_list", () -> addressClient.list(authorization));
    }

    /**
     * 查询一条收货地址详情。
     */
    @McpTool(
            name = "address_get_detail",
            title = "查询地址详情",
            description = "根据地址ID查询当前登录用户的一条收货地址详情。",
            annotations = @McpTool.McpAnnotations(
                    title = "查询地址详情",
                    readOnlyHint = true,
                    destructiveHint = false,
                    idempotentHint = true,
                    openWorldHint = false
            )
    )
    public String getDetail(
            McpSyncRequestContext context,
            @McpToolParam(description = "地址ID", required = true) Long addressId) {
        String authorization = McpAuthorization.required(context);
        return clientExecutor.execute(
                "address_get_detail",
                () -> addressClient.getDetail(authorization, addressId)
        );
    }

    /**
     * 新增收货地址。
     */
    @McpTool(
            name = "address_add",
            title = "新增收货地址",
            description = "为当前登录用户新增收货地址。收货信息完整后直接调用。",
            annotations = @McpTool.McpAnnotations(
                    title = "新增收货地址",
                    readOnlyHint = false,
                    destructiveHint = false,
                    idempotentHint = false,
                    openWorldHint = false
            )
    )
    public String add(
            McpSyncRequestContext context,
            @McpToolParam(description = "新增地址信息，addressId应为空", required = true)
            AddressRequest request) {
        String authorization = McpAuthorization.required(context);
        return clientExecutor.execute(
                "address_add",
                () -> addressClient.add(authorization, toMall4jRequest(request))
        );
    }

    /**
     * 修改收货地址。
     */
    @McpTool(
            name = "address_update",
            title = "修改收货地址",
            description = "修改当前登录用户的收货地址。addressId和修改后的完整信息明确后直接调用。",
            annotations = @McpTool.McpAnnotations(
                    title = "修改收货地址",
                    readOnlyHint = false,
                    destructiveHint = false,
                    idempotentHint = true,
                    openWorldHint = false
            )
    )
    public String update(
            McpSyncRequestContext context,
            @McpToolParam(description = "修改后的完整地址信息", required = true)
            AddressRequest request) {
        if (request.addressId() == null) {
            throw new IllegalArgumentException("修改地址时 addressId 不能为空");
        }
        String authorization = McpAuthorization.required(context);
        return clientExecutor.execute(
                "address_update",
                () -> addressClient.update(authorization, toMall4jRequest(request))
        );
    }

    /**
     * 删除非默认收货地址。
     */
    @McpTool(
            name = "address_delete",
            title = "删除收货地址",
            description = "删除当前登录用户的一条非默认收货地址。目标地址明确后直接调用，系统会在执行前通过审批界面确认。",
            annotations = @McpTool.McpAnnotations(
                    title = "删除收货地址",
                    readOnlyHint = false,
                    destructiveHint = true,
                    idempotentHint = true,
                    openWorldHint = false
            )
    )
    public String delete(
            McpSyncRequestContext context,
            @McpToolParam(description = "需要删除的地址ID", required = true) Long addressId) {
        String authorization = McpAuthorization.required(context);
        return clientExecutor.execute(
                "address_delete",
                () -> addressClient.delete(authorization, addressId)
        );
    }

    /**
     * 设置默认收货地址。
     */
    @McpTool(
            name = "address_set_default",
            title = "设置默认地址",
            description = "将当前登录用户的一条收货地址设为默认地址。目标地址明确后直接调用。",
            annotations = @McpTool.McpAnnotations(
                    title = "设置默认地址",
                    readOnlyHint = false,
                    destructiveHint = false,
                    idempotentHint = true,
                    openWorldHint = false
            )
    )
    public String setDefault(
            McpSyncRequestContext context,
            @McpToolParam(description = "需要设为默认的地址ID", required = true) Long addressId) {
        String authorization = McpAuthorization.required(context);
        return clientExecutor.execute(
                "address_set_default",
                () -> addressClient.setDefault(authorization, addressId)
        );
    }

    private Map<String, Object> toMall4jRequest(AddressRequest request) {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("addrId", request.addressId());
        body.put("receiver", request.receiver());
        body.put("addr", request.detailAddress());
        body.put("postCode", request.postCode());
        body.put("mobile", request.mobile());
        body.put("provinceId", request.provinceId());
        body.put("cityId", request.cityId());
        body.put("areaId", request.areaId());
        body.put("province", request.province());
        body.put("city", request.city());
        body.put("area", request.area());
        return body;
    }
}
