package com.stocktrum.backend.features.user.api;

import com.stocktrum.backend.core.security.UserPrincipal;
import com.stocktrum.backend.features.user.api.dto.DeleteAccountDTO;
import com.stocktrum.backend.features.user.service.UserService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/user")
public class UserController {
  private final UserService userService;

  public UserController(UserService userService) {
    this.userService = userService;
  }

  /** Deletes the authenticated user's account, after verifying their password. */
  @PostMapping("/delete")
  public ResponseEntity<Void> delete(
      @AuthenticationPrincipal UserPrincipal me, @Valid @RequestBody DeleteAccountDTO req) {
    userService.deleteSelf(me.getId(), req.password());
    return ResponseEntity.noContent().build();
  }
}
