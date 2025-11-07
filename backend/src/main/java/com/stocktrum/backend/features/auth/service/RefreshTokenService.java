package com.stocktrum.backend.features.auth.service;

import com.stocktrum.backend.features.auth.domain.RefreshToken;
import com.stocktrum.backend.features.auth.domain.exception.InvalidRefreshTokenException;
import com.stocktrum.backend.features.auth.domain.exception.RefreshTokenExpiredOrRevokedException;
import com.stocktrum.backend.features.auth.repo.RefreshTokenRepository;
import com.stocktrum.backend.features.user.domain.User;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.security.SecureRandom;
import java.time.Duration;
import java.time.Instant;
import java.util.Base64;

@Service
public class RefreshTokenService {

  private final RefreshTokenRepository repo;
  private final SecureRandom random = new SecureRandom();

  // 30 days by default
  private static final Duration REFRESH_TTL = Duration.ofDays(30);

  public RefreshTokenService(RefreshTokenRepository repo) {
    this.repo = repo;
  }

  /**
   * Issues a new refresh token for the given user.
   *
   * <p>The token is stored hashed (server-side lookup by token hash), and the raw token is returned
   * to the caller for secure storage (e.g., HTTP-only cookie).
   *
   * @param user the user to assign the refresh token to
   * @return the newly created refresh token entity
   */
  public RefreshToken create(User user) {
    String token = generateOpaqueToken();
    Instant now = Instant.now();
    RefreshToken rt = new RefreshToken(token, user, now, now.plus(REFRESH_TTL));
    return repo.save(rt);
  }

  /**
   * Rotates a valid refresh token, revoking the old one and issuing a new one.
   *
   * <p>Rotation protects against replay: if an attacker steals a refresh token, the real user’s next
   * refresh will invalidate it.
   *
   * @param oldTokenStr the raw refresh token presented by the client
   * @return the newly issued refresh token
   * @throws InvalidRefreshTokenException if the token does not exist
   * @throws RefreshTokenExpiredOrRevokedException if the token is expired or no longer active
   */
  @Transactional
  public RefreshToken rotate(String oldTokenStr) {
    RefreshToken old =
        repo.findByTokenHash(oldTokenStr)
            .orElseThrow(() -> new InvalidRefreshTokenException("Invalid refresh token"));

    if (!old.isActiveAt(Instant.now()) || old.getExpiresAt().isBefore(Instant.now())) {
      throw new RefreshTokenExpiredOrRevokedException("Refresh token expired or revoked");
    }

    // Set up new refresh token
    RefreshToken fresh = create(old.getUser());
    old.setRevokedAt(Instant.now());
    old.setReplacedById(fresh.getId());
    repo.save(old);

    return fresh;
  }

  /**
   * Revokes a single refresh token (e.g., logout on a single device).
   *
   * @param tokenStr raw refresh token
   */
  @Transactional
  public void revoke(String tokenStr) {
    repo.findByTokenHash(tokenStr)
        .ifPresent(
            rt -> {
              rt.setRevokedAt(Instant.now());
              repo.save(rt);
            });
  }

  /**
   * Revokes all refresh tokens for a user (e.g., global logout).
   *
   * @param userId the user whose tokens should be revoked
   * @return number of tokens revoked
   */
  @Transactional
  public long revokeAllForUser(long userId) {
    return repo.deleteByUser_UserId(userId);
  }

  private String generateOpaqueToken() {
    byte[] bytes = new byte[32]; // 256-bit
    random.nextBytes(bytes);
    return Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);
  }
}
