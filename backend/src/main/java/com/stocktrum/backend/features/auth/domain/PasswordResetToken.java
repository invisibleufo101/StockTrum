package com.stocktrum.backend.features.auth.domain;

import com.stocktrum.backend.features.user.domain.User;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.Instant;
import java.util.UUID;

@Entity
@Getter
@Setter
@Table(
    name = "password_reset_token",
    indexes = {
      @Index(name = "idx_prt_user", columnList = "user_id"),
      @Index(name = "idx_prt_expires", columnList = "expires_at"),
      @Index(name = "idx_prt_used", columnList = "used_at")
    },
    uniqueConstraints = {@UniqueConstraint(name = "uk_prt_token_hash", columnNames = "token_hash")})
public class PasswordResetToken {

  @Id
  @GeneratedValue
  @JdbcTypeCode(SqlTypes.UUID)
  private UUID id;

  @ManyToOne(optional = false, fetch = FetchType.LAZY)
  @JoinColumn(name = "user_id", nullable = false, foreignKey = @ForeignKey(name = "fk_prt_user"))
  private User user;

  @Column(name = "token_selector", nullable = false, unique = true, length = 64)
  private String selector;

  // SHA-256 hex (64 chars) to match your refresh-token style
  @Column(name = "validator_hash", nullable = false, unique = true, length = 64)
  private String validatorHash;

  @Column(name = "requested_at", nullable = false, updatable = false)
  private Instant requestedAt;

  @Column(name = "expires_at", nullable = false)
  private Instant expiresAt;

  @Column(nullable = false)
  private boolean used = false;
}
