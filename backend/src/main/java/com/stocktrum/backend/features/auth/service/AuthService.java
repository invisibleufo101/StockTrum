package com.stocktrum.backend.features.auth.service;

import com.stocktrum.backend.core.security.UserPrincipal;
import com.stocktrum.backend.core.security.jwt.JWTService;
import com.stocktrum.backend.features.auth.domain.AccessAndRefreshTokens;
import com.stocktrum.backend.features.auth.domain.RefreshToken;
import com.stocktrum.backend.features.auth.api.dto.UserRegisterDTO;
import com.stocktrum.backend.features.user.domain.User;
import com.stocktrum.backend.features.user.repo.UserRepository;
import com.stocktrum.backend.features.user.repo.UserRoleRepository;
import org.springframework.security.crypto.password.PasswordEncoder;
import jakarta.transaction.Transactional;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Service;

@Service
public class AuthService {
  private final AuthenticationManager authManager;
  private final JWTService jwtService;
  private final RefreshTokenService refreshService;
  private final UserRepository userRepository;
  private final PasswordEncoder passwordEncoder;
  private final UserRoleRepository userRole;

  public AuthService(
      AuthenticationManager authManager,
      JWTService jwtService,
      RefreshTokenService refreshToken,
      UserRepository userRepository,
      PasswordEncoder passwordEncoder,
      UserRoleRepository userRole) {
    this.authManager = authManager;
    this.jwtService = jwtService;
    this.refreshService = refreshToken;
    this.userRepository = userRepository;
    this.passwordEncoder = passwordEncoder;
    this.userRole = userRole;
  }

  /**
   * Authenticates the user with email and password, and returns new access & refresh tokens.
   *
   * @param email user login email
   * @param password raw password provided by the user
   * @return newly generated access token + refresh token
   */
  @Transactional
  public AccessAndRefreshTokens login(String email, String password) {
    Authentication auth =
        authManager.authenticate(new UsernamePasswordAuthenticationToken(email, password));
    UserPrincipal principal = (UserPrincipal) auth.getPrincipal();

    // Build tokens
    String accessToken = jwtService.generateAccessToken(principal.getUser());

    RefreshToken refreshToken = refreshService.create(principal.getUser());

    return new AccessAndRefreshTokens(accessToken, refreshToken);
  }

  /**
   * Rotates an existing refresh token and issues a new access token.
   *
   * @param refreshString the raw refresh token from cookie
   * @return new access token + the newly rotated refresh token
   */
  @Transactional
  public AccessAndRefreshTokens refresh(String refreshString) {
    RefreshToken fresh = refreshService.rotate(refreshString);
    String access = jwtService.generateAccessToken(fresh.getUser());
    return new AccessAndRefreshTokens(access, fresh);
  }

  public void registerUser(UserRegisterDTO register) {
    if (userRepository.existsByEmail(register.getEmail())) {
      throw new BadCredentialsException("Email already exists");
    }

    User user = new User();
    user.setNickname(register.getNickname());
    user.setEmail(register.getEmail());
    user.setPassword(passwordEncoder.encode(register.getPassword()));
    user.setUserRole(userRole.findByRoleName("user"));

    userRepository.save(user);
  }
}
