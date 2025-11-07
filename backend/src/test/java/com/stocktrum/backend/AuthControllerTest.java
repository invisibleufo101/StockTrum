package com.stocktrum.backend;


import com.fasterxml.jackson.databind.ObjectMapper;
import com.stocktrum.backend.core.exception.GlobalExceptionHandler;
import com.stocktrum.backend.core.security.jwt.JWTFilter;
import com.stocktrum.backend.core.util.CookieWriter;
import com.stocktrum.backend.features.auth.api.AuthController;
import com.stocktrum.backend.features.auth.api.dto.UserLoginDTO;
import com.stocktrum.backend.features.auth.domain.AccessAndRefreshTokens;
import com.stocktrum.backend.features.auth.domain.RefreshToken;
import com.stocktrum.backend.features.auth.service.AuthService;
import com.stocktrum.backend.features.auth.service.PasswordResetService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.FilterType;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.DisabledException;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.containsString;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(
    controllers = AuthController.class,
    excludeFilters = @ComponentScan.Filter(type = FilterType.ASSIGNABLE_TYPE, classes = JWTFilter.class)
)
@Import({CookieWriter.class, GlobalExceptionHandler.class})
@AutoConfigureMockMvc(addFilters = false)
class AuthControllerTest {

  @Autowired MockMvc mvc;
  @Autowired ObjectMapper om; // to build JSON easily
  @Autowired CookieWriter cookies;


  @MockitoBean AuthService authService;
  @MockitoBean PasswordResetService passwordResetService;



  @Test
  void login_success_200_accessToken_and_cookie() throws Exception {
    String email = "ok@ex.com";
    String password = "secret";

    AccessAndRefreshTokens tokens = mock(AccessAndRefreshTokens.class);
    RefreshToken refresh = mock(RefreshToken.class);

    when(tokens.accessToken()).thenReturn("ACCESS_123");
    when(tokens.refreshToken()).thenReturn(refresh);
    when(refresh.getTokenHash()).thenReturn("REFRESH_HASH");

    when(authService.login(eq(email), eq(password))).thenReturn(tokens);

    String body = om.writeValueAsString(new UserLoginDTO(email, password));

    mvc.perform(post("/api/auth/login")
            .contentType(MediaType.APPLICATION_JSON)
            .content(body))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.accessToken").value("ACCESS_123"))
        .andExpect(header().string("Set-Cookie",
            allOf(
                containsString("refresh_token=REFRESH_HASH"),
                containsString("HttpOnly"),
                containsString("Secure"),
                containsString("Path=/api/auth"),
                containsString("SameSite=Strict"),
                containsString("Max-Age=2592000") // 30 days
            )
        ));
  }

  @Test
  void login_returns401_onBadCredentials() throws Exception {
    String email = "wrong@ex.com";
    String password = "wrong";

    when(authService.login(eq(email), eq(password)))
        .thenThrow(new BadCredentialsException("Bad credentials"));

    String body = om.writeValueAsString(new UserLoginDTO(email, password));

    mvc.perform(post("/api/auth/login")
            .contentType(MediaType.APPLICATION_JSON)
            .content(body))
        .andExpect(status().isUnauthorized())
        .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_JSON))
        .andExpect(jsonPath("$.code").value("BAD_CREDENTIALS"))
        .andExpect(jsonPath("$.message").value("Bad credentials"))
        // no refresh cookie on failure:
        .andExpect(header().doesNotExist("Set-Cookie"));
  }

  @Test
  void login_return403_whenUserIsBanned() throws Exception {
    String email = "banned@ex.com";
    String password = "secret";

    when(authService.login(eq(email), eq(password)))
        .thenThrow(new DisabledException("Bad credentials"));

    String body = om.writeValueAsString(new UserLoginDTO(email, password));

    mvc.perform(post("/api/auth/login")
            .contentType(MediaType.APPLICATION_JSON)
            .content(body))
        .andExpect(status().isUnauthorized())
        .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_JSON))
        .andExpect(jsonPath("$.code").value("ACCOUNT_DISABLED"))
        .andExpect(jsonPath("$.message").value("Account is disabled"))
        // no refresh cookie on failure:
        .andExpect(header().doesNotExist("Set-Cookie"));

  }
}









