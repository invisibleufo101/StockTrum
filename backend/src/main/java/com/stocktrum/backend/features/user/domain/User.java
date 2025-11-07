package com.stocktrum.backend.features.user.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import org.hibernate.annotations.ColumnTransformer;

import java.time.LocalDateTime;

@Entity
@Getter
@Setter
@Table(name = "users")
public class User {

  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  @Column(name = "user_id")
  private Long userId;

  @Enumerated(EnumType.STRING)
  @Column(name = "status", columnDefinition = "user_status DEFAULT 'Active'")
  @ColumnTransformer(write = "?::user_status")
  private UserStatus status = UserStatus.Active;

  @ManyToOne(fetch = FetchType.EAGER)
  @JoinColumn(name = "role_id")
  private UserRole userRole;

  @Column(name = "email", nullable = false, unique = true)
  private String email;

  @Column(name = "password", nullable = false, length = 64)
  private String password;

  @Column(name = "nickname", length = 15)
  private String nickname;

  @Column(name = "created_at", columnDefinition = "TIMESTAMP DEFAULT now()")
  private LocalDateTime createdAt = LocalDateTime.now();

  @Column(name = "deleted_at")
  private LocalDateTime deletedAt;

  @Column(name = "token_version", nullable = false)
  private int tokenVersion = 0;
}
