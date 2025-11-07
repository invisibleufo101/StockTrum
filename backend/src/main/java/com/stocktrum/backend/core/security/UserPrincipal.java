package com.stocktrum.backend.core.security;

import com.stocktrum.backend.features.user.domain.User;
import com.stocktrum.backend.features.user.domain.UserStatus;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.util.Collection;
import java.util.Collections;

public class UserPrincipal implements UserDetails {

  private final User user;

  public UserPrincipal(User user) {
    this.user = user;
  }

  // Spring Security calls this during authentication. Throws DisabledException if False.
  @Override
  public boolean isEnabled() {
    return user.getStatus() == UserStatus.Active;
  }

  @Override
  public boolean isCredentialsNonExpired() {
    return true;
  }

  @Override
  public boolean isAccountNonLocked() {
    return true;
  }

  @Override
  public boolean isAccountNonExpired() {
    return true;
  }

  @Override
  public String getUsername() {
    return user.getEmail();
  }

  public User getUser() {
    return user;
  }

  @Override
  public String getPassword() {
    return user.getPassword();
  }

  @Override
  public Collection<? extends GrantedAuthority> getAuthorities() {
    return Collections.singleton(new SimpleGrantedAuthority("ROLE_" + user.getUserRole()));
  }

  public int getTokenVersion() {
    return user.getTokenVersion();
  }

  public long getId() {
    return user.getUserId();
  }
}
