package com.stocktrum.backend.features.auth.domain.exception;

public class InvalidRefreshTokenException extends RuntimeException {
  public InvalidRefreshTokenException(String msg) {
    super(msg);
  }
}
