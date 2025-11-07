package com.stocktrum.backend.features.auth.api.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class UserLoginDTO {

  @NotBlank(message = "email is required")
  private String email;

  @NotBlank(message = "Password is required")
  private String password;

  public UserLoginDTO(String mail, String pw) {
    this.email = mail;
    this.password = pw;
  }
}
