package com.yami.shop.security.admin.adapter;

import com.yami.shop.security.common.adapter.DefaultAuthConfigAdapter;
import org.springframework.stereotype.Component;

import java.util.Arrays;
import java.util.List;

/**
 * 单体应用的授权路径配置。
 *
 * <p>yami-shop-admin 是唯一启动模块，管理端与用户端接口在同一个上下文、同一个端口下运行，
 * 因此放行路径需要同时包含两端原本各自放行的地址：管理端的文档、验证码、管理员登录，
 * 以及用户端的登录、登出、Token 刷新和免登录浏览接口（商品、分类、公告、搜索等）。
 * 其余地址（如 /sys/**、/admin/**、/p/**）仍然需要携带 Token。</p>
 *
 * @author 菠萝凤梨
 * @date 2022/3/28 14:57
 */
@Component
public class ResourceServerAdapter extends DefaultAuthConfigAdapter {
    public static final List<String> EXCLUDE_PATH = Arrays.asList(
            // 接口文档与静态资源
            "/webjars/**",
            "/swagger/**",
            "/v3/api-docs/**",
            "/doc.html",
            "/swagger-ui.html",
            "/swagger-resources/**",
            "/mall4j/img/**",
            // 验证码、管理员登录
            "/captcha/**",
            "/adminLogin",
            // 用户端登录、登出、刷新 Token
            "/login",
            "/logOut",
            "/token/refresh",
            // 用户端免登录接口
            "/indexImgs",
            "/category/categoryInfo",
            "/delivery/check",
            "/search/**",
            "/sku/getSkuList",
            "/user/register",
            "/user/updatePwd",
            "/shop/notice/topNoticeList",
            "/shop/notice/noticeList",
            "/shop/notice/info/*",
            "/prod/pageProd",
            "/prod/prodInfo",
            "/prod/lastedProdPage",
            "/prod/prodListByTagId",
            "/prod/moreBuyProdList",
            "/prod/tagProdList",
            "/prod/tag/prodTagList",
            "/prodComm/**");

    @Override
    public List<String> excludePathPatterns() {
        return EXCLUDE_PATH;
    }
}
