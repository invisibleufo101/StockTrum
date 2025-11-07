package com.stocktrum.backend.features.auth.api;

import com.stocktrum.backend.core.util.CookieWriter;
import com.stocktrum.backend.features.auth.api.dto.TokenResponseDTO;
import com.stocktrum.backend.features.auth.api.dto.UserLoginDTO;
import com.stocktrum.backend.features.auth.domain.AccessAndRefreshTokens;
import com.stocktrum.backend.features.auth.service.AuthService;
import com.stocktrum.backend.features.auth.api.dto.UserRegisterDTO;
import com.stocktrum.backend.features.auth.api.dto.ForgotPasswordRequest;
import com.stocktrum.backend.features.auth.api.dto.ResetPasswordRequest;
import com.stocktrum.backend.features.auth.service.PasswordResetService;

import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import jakarta.servlet.http.HttpServletResponse;
import java.time.Duration;

@RestController
@RequestMapping("/api/auth")
public class AuthController {
  private final AuthService authService;
  private final CookieWriter cookies;
  private final PasswordResetService passwordResetService;

  public AuthController(
      AuthService authService, CookieWriter cookies, PasswordResetService passwordResetService) {
    this.cookies = cookies;
    this.authService = authService;
    this.passwordResetService = passwordResetService;
  }

  /** Authenticates a user and returns an access token + sets refresh token cookie. */
  @PostMapping("/login")
  public ResponseEntity<TokenResponseDTO> login(
      @RequestBody UserLoginDTO login, HttpServletResponse response) {

    AccessAndRefreshTokens result = authService.login(login.getEmail(), login.getPassword());

    cookies.writeRefresh(response, result.refreshToken().getTokenHash(), Duration.ofDays(30));

    return ResponseEntity.ok(new TokenResponseDTO(result.accessToken()));
  }

  /** Registers a new user account. */
  @PostMapping("/register")
  public ResponseEntity<TokenResponseDTO> register(
      @RequestBody UserRegisterDTO register, HttpServletResponse response) {
    authService.registerUser(register);
    return ResponseEntity.status(HttpStatus.CREATED).build();
  }

  /** Exchanges a valid refresh token cookie for a new access token (session continuation). */
  @PostMapping("refresh")
  public ResponseEntity<TokenResponseDTO> refresh(
      @CookieValue(value = "refresh_token", required = false) String refreshString,
      HttpServletResponse response) {
    if (refreshString == null) {
      return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
    }

    AccessAndRefreshTokens result = authService.refresh(refreshString);
    cookies.writeRefresh(response, result.refreshToken().getTokenHash(), Duration.ofDays(30));

    return ResponseEntity.ok(new TokenResponseDTO(result.accessToken()));
  }

  /** Sends a password reset email if the account exists. (Always returns 200 to prevent ID leaks.) */
  @PostMapping("/forgot")
  public ResponseEntity<Void> forgot(@Valid @RequestBody ForgotPasswordRequest req) {
    passwordResetService.requestReset(req.email());
    return ResponseEntity.ok().build(); // always 200
  }

  /** Resets password using a valid reset token. */
  @PostMapping("/reset")
  public ResponseEntity<Void> reset(@Valid @RequestBody ResetPasswordRequest req) {
    passwordResetService.reset(req.token(), req.newPassword());
    return ResponseEntity.noContent().build();
  }
}
