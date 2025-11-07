package com.stocktrum.backend.features.auth.service;

import com.stocktrum.backend.core.util.CookieWriter;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.security.web.authentication.logout.LogoutHandler;
import org.springframework.stereotype.Component;
import org.springframework.web.util.WebUtils;

@Component
@RequiredArgsConstructor
public class RefreshTokenLogoutHandler implements LogoutHandler {
  private final RefreshTokenService refreshTokenService;
  private final CookieWriter cookieWriter;

  @Override
  public void logout(HttpServletRequest req, HttpServletResponse res, Authentication auth) {
    // Read refresh cookie
    var cookie = WebUtils.getCookie(req, "refresh_token");

    // Revoke in DB
    if (cookie != null && cookie.getValue() != null && !cookie.getValue().isBlank()) {
      refreshTokenService.revoke(cookie.getValue());
    }

    // Clear cookie on client
    cookieWriter.clearRefresh(res);
  }
}
