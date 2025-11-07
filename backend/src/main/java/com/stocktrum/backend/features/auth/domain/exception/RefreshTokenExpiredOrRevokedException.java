package com.stocktrum.backend.features.auth.domain.exception;

public class RefreshTokenExpiredOrRevokedException extends RuntimeException {
  public RefreshTokenExpiredOrRevokedException(String msg) {
    super(msg);
  }
}
