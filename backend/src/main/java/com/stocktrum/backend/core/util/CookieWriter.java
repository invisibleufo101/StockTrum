package com.stocktrum.backend.core.util;

import jakarta.servlet.http.HttpServletResponse;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseCookie;
import org.springframework.stereotype.Component;

import java.time.Duration;

@Component
public class CookieWriter {
  public static final String REFRESH_TOKEN = "refresh_token";

  public void writeRefresh(HttpServletResponse response, String raw, Duration maxAge) {
    ResponseCookie cookie =
        ResponseCookie.from(REFRESH_TOKEN, raw)
            .httpOnly(true)
            .secure(true) // set true in prod; for local HTTP you may toggle
            .sameSite("Strict")
            .path("/api/auth")
            .maxAge(maxAge)
            .build();
    response.addHeader(HttpHeaders.SET_COOKIE, cookie.toString());
  }

  public void clearRefresh(HttpServletResponse response) {
    ResponseCookie cookie =
        ResponseCookie.from(REFRESH_TOKEN, "")
            .httpOnly(true)
            .secure(true)
            .sameSite("Strict")
            .path("/api/auth")
            .maxAge(Duration.ZERO)
            .build();
    response.addHeader(HttpHeaders.SET_COOKIE, cookie.toString());
  }
}
