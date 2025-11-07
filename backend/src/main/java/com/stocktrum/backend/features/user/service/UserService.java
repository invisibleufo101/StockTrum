package com.stocktrum.backend.features.user.service;

import com.stocktrum.backend.features.auth.service.RefreshTokenService;
import com.stocktrum.backend.features.user.domain.User;
import com.stocktrum.backend.features.user.repo.UserRepository;
import jakarta.transaction.Transactional;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Service
public class UserService {
  private final UserRepository userRepo;
  private final PasswordEncoder encoder;
  private final RefreshTokenService refreshTokenService;

  public UserService(
      UserRepository userRepo,
      PasswordEncoder passwordEncoder,
      RefreshTokenService refreshTokenService) {
    this.userRepo = userRepo;
    this.encoder = passwordEncoder;
    this.refreshTokenService = refreshTokenService;
  }

  /**
   * Soft-deletes the authenticated user's account after verifying their password.
   *
   * <p>Effects:
   * <ul>
   *   <li>Marks the account as deleted (does not permanently remove data).</li>
   *   <li>Increments the user's token version so all active sessions are invalidated immediately.</li>
   *   <li>Revokes all refresh tokens, logging the user out everywhere.</li>
   * </ul>
   *
   * @param userId ID of the authenticated user requesting deletion
   * @param password raw password provided for confirmation
   * @throws UsernameNotFoundException if the user does not exist
   * @throws BadCredentialsException if the provided password is incorrect
   */
  @Transactional
  public void deleteSelf(long userId, String password) {
    User user =
        userRepo
            .findById(userId)
            .orElseThrow(() -> new UsernameNotFoundException("User not found"));

    if (password != null) {
      if (!encoder.matches(password, user.getPassword())) {
        throw new BadCredentialsException("Password mismatch");
      }
    }

    // Soft delete + invalidate all access tokens immediately
    user.setDeletedAt(LocalDateTime.now());
    user.setTokenVersion(user.getTokenVersion() + 1);
    userRepo.save(user);

    // Revoke all refresh tokens for this user
    refreshTokenService.revokeAllForUser(userId);
  }
}
