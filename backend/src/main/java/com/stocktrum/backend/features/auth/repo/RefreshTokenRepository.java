package com.stocktrum.backend.features.auth.repo;

import com.stocktrum.backend.features.auth.domain.RefreshToken;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;
import java.util.UUID;

public interface RefreshTokenRepository extends JpaRepository<RefreshToken, UUID> {
  Optional<RefreshToken> findByTokenHash(String tokenHash);

  long deleteByUser_UserId(Long userId);
}
