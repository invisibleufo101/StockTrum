package com.stocktrum.backend.core.config;

import com.stocktrum.backend.core.security.jwt.JWTFilter;
import com.stocktrum.backend.core.security.CustomUserDetailsService;
import com.stocktrum.backend.features.auth.service.RefreshTokenLogoutHandler;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.AuthenticationProvider;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

  private CustomUserDetailsService customUserDetailsService;
  private JWTFilter jwtFilter;
  private final RefreshTokenLogoutHandler refreshTokenLogoutHandler;

  public SecurityConfig(
      RefreshTokenLogoutHandler refreshTokenLogoutHandler,
      CustomUserDetailsService customUserDetailsService,
      JWTFilter jwtFilter) {
    this.refreshTokenLogoutHandler = refreshTokenLogoutHandler;
    this.customUserDetailsService = customUserDetailsService;
    this.jwtFilter = jwtFilter;
  }

  @Bean
  public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {

    http.csrf(csrf -> csrf.disable())
        .sessionManagement(
            session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
        .authorizeHttpRequests(
            reg ->
                reg.requestMatchers(
                        "/api/auth/login",
                        "/api/auth/refresh",
                        "/api/auth/register",
                        "/api/auth/forgot",
                        "/api/auth/reset",
                        "/api/auth/logout")
                    .permitAll()
                    .requestMatchers("/user/**")
                    .hasAnyRole("user")
                    .requestMatchers("/admin/**")
                    .hasRole("admin")
                    .anyRequest()
                    .authenticated())
        .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class)
        .logout(
            logout ->
                logout
                    .logoutUrl("/api/auth/logout")
                    .addLogoutHandler(refreshTokenLogoutHandler)
                    .logoutSuccessHandler(
                        (req, res, auth) -> res.setStatus(HttpServletResponse.SC_NO_CONTENT)));

    return http.build();
  }

  // One encoder for the whole app)
  @Bean
  public PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder(12);
  }

  @Bean
  public AuthenticationProvider authenticationProvider(PasswordEncoder passwordEncoder) {
    DaoAuthenticationProvider provider = new DaoAuthenticationProvider();
    provider.setPasswordEncoder(passwordEncoder);
    provider.setUserDetailsService(customUserDetailsService);
    return provider;
  }

  @Bean
  public AuthenticationManager authenticationManager(AuthenticationConfiguration config)
      throws Exception {
    return config.getAuthenticationManager();
  }
}
