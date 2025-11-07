package com.stocktrum.backend.core.exception;

import com.stocktrum.backend.features.auth.domain.exception.InvalidRefreshTokenException;
import com.stocktrum.backend.features.auth.domain.exception.RefreshTokenExpiredOrRevokedException;
import com.stocktrum.backend.features.auth.domain.exception.UserBannedException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.DisabledException;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;

import java.time.Instant;

@RestControllerAdvice
public class GlobalExceptionHandler {

  // Small, consistent error body
  public record ErrorBody(String code, String message, Instant timestamp) {
    public static ErrorBody of(String code, String message) {
      return new ErrorBody(code, message, Instant.now());
    }
  }

  @ExceptionHandler(InvalidRefreshTokenException.class)
  public ResponseEntity<ErrorBody> invalid(InvalidRefreshTokenException ex) {
    return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
        .body(ErrorBody.of("INVALID_REFRESH_TOKEN", ex.getMessage()));
  }

  @ExceptionHandler(RefreshTokenExpiredOrRevokedException.class)
  public ResponseEntity<ErrorBody> expired(RefreshTokenExpiredOrRevokedException ex) {
    return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
        .body(ErrorBody.of("TOKEN_EXPIRED_OR_REVOKED", ex.getMessage()));
  }

  @ExceptionHandler(UserBannedException.class)
  public ResponseEntity<ErrorBody> banned(UserBannedException ex) {
    return ResponseEntity.status(HttpStatus.FORBIDDEN)
        .body(ErrorBody.of("USER_BANNED", ex.getMessage()));
  }

  @ExceptionHandler(BadCredentialsException.class)
  public ResponseEntity<ErrorBody> handleBadCredentials(BadCredentialsException ex) {
    return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
        .body(ErrorBody.of("BAD_CREDENTIALS", ex.getMessage()));
  }

  @ExceptionHandler(DisabledException.class)
  public ResponseEntity<ErrorBody> handleDisabledException(DisabledException ex) {
    return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
        .body(ErrorBody.of("ACCOUNT_DISABLED", "Account is disabled"));
  }
}
