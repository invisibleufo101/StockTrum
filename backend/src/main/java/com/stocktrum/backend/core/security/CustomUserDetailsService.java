package com.stocktrum.backend.core.security;

import com.stocktrum.backend.features.user.domain.User;
import com.stocktrum.backend.features.user.repo.UserRepository;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

@Service
public class CustomUserDetailsService implements UserDetailsService {

  private UserRepository userRepo;

  public CustomUserDetailsService(UserRepository userRepo) {
    this.userRepo = userRepo;
  }

  @Override
  public UserDetails loadUserByUsername(String email) throws UsernameNotFoundException {
    User user = userRepo.findByEmail(email).orElseThrow(() -> new UsernameNotFoundException(email));

    return new UserPrincipal(user);
  }

  // load by ID carried in JWT sub
  public UserDetails loadUserById(String sub) {
    long userId = Long.parseLong(sub);
    User user =
        userRepo
            .findUserByUserId(userId)
            .orElseThrow(() -> new UsernameNotFoundException("User not found: " + sub));
    return new UserPrincipal(user);
  }
}
