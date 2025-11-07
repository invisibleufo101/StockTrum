package com.stocktrum.backend.features.auth.domain.exception;

public class UserBannedException extends RuntimeException {
  public UserBannedException() {
    super("User is banned");
  }
}
