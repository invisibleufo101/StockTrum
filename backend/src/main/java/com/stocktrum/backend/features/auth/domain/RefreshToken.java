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
    name = "refresh_tokens",
    indexes = {
      @Index(name = "idx_refresh_token_hash", columnList = "token_hash", unique = true),
      @Index(name = "idx_refresh_user_active", columnList = "user_id, expires_at, revoked_at")
    })
public class RefreshToken {

  @Id
  @GeneratedValue
  @JdbcTypeCode(SqlTypes.UUID)
  private UUID id;

  // store only the hash of the opaque token (e.g., SHA-256 hex => 64 chars)
  @Column(name = "token_hash", nullable = false, unique = true, length = 64)
  private String tokenHash;

  @ManyToOne(optional = false, fetch = FetchType.LAZY)
  @JoinColumn(
      name = "user_id",
      nullable = false,
      foreignKey = @ForeignKey(name = "fk_refresh_token_user"))
  private User user;

  @Column(name = "issued_at", nullable = false)
  private Instant issuedAt;

  @Column(name = "expires_at", nullable = false)
  private Instant expiresAt;

  // null means still active; non-null means revoked at this moment
  @Column(name = "revoked_at")
  private Instant revokedAt;

  // rotation linking: the new token that replaced this one
  @JdbcTypeCode(SqlTypes.UUID)
  @Column(name = "replaced_by_id")
  private UUID replacedById;

  public RefreshToken() {}

  public RefreshToken(String tokenHash, User user, Instant issuedAt, Instant expiresAt) {
    this.tokenHash = tokenHash;
    this.user = user;
    this.issuedAt = issuedAt;
    this.expiresAt = expiresAt;
  }

  public boolean isActiveAt(Instant now) {
    return (revokedAt == null) && now.isBefore(expiresAt);
  }

  public Object getToken() {
    return null;
  }
}
