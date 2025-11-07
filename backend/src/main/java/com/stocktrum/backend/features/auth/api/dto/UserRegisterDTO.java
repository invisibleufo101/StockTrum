package com.stocktrum.backend.features.auth.api.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class UserRegisterDTO {

  @NotBlank(message = "Nickname is required")
  private String nickname;

  @NotBlank(message = "Email is required")
  private String email;

  @NotBlank(message = "Password is required")
  private String password;

  public UserRegisterDTO(String nickname, String mail, String pw) {
    this.nickname = nickname;
    this.email = mail;
    this.password = pw;
  }
}
