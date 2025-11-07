// Intercepts requests and applies authentication.

package com.stocktrum.backend.core.security.jwt;

import com.stocktrum.backend.core.security.CustomUserDetailsService;
import com.stocktrum.backend.core.security.UserPrincipal;
import io.jsonwebtoken.Claims;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

@Component
public class JWTFilter extends OncePerRequestFilter {

  @Autowired private JWTService jwtService;

  @Autowired private CustomUserDetailsService userDetailsService;

  @Override
  protected void doFilterInternal(
      HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
      throws ServletException, IOException {

    // 1) Read Authorization header and verify "Bearer " prefix.
    final String authHeader = request.getHeader("Authorization");
    if (authHeader == null || !authHeader.startsWith("Bearer ")) {
      // No JWT present → proceed without authentication.
      filterChain.doFilter(request, response);
      return;
    }

    // 2) Extract the raw JWT (strip "Bearer ").
    String token = authHeader.substring(7);

    // 3) Parse + verify the token (signature, expiration, audience, etc.).
    Claims claims;
    try {
      // Verify signature + parse claims
      claims = jwtService.parseAndValidate(token); // throws if bad signature/expired
    } catch (Exception e) {
      filterChain.doFilter(request, response);
      return;
    }

    // 4) Extract the subject (user identifier). If absent, continue unauthenticated.
    final String sub = claims.getSubject();
    if (sub == null) {
      filterChain.doFilter(request, response);
      return;
    }

    // 5) Read token-version (tv) claim. Default to 0 for back-compat if not present.
    Integer tvClaim = claims.get("tv", Integer.class);
    final int tokenVersionInJwt = (tvClaim != null) ? tvClaim : 0;

    // 6) Only build Authentication if the context is currently unauthenticated.
    if (SecurityContextHolder.getContext().getAuthentication() == null) {
      // Load the current user by subject (e.g., userId from your JWT "sub" claim).
      UserDetails userDetails = userDetailsService.loadUserById(sub);

      // If your UserDetails is a custom principal, enforce soft-delete + token-version checks.
      if (userDetails instanceof UserPrincipal aud) {
        // 6a) Block soft-deleted users immediately.
        if (!aud.isEnabled()) {
          // Immediately block deleted accounts
          SecurityContextHolder.clearContext();

          filterChain.doFilter(request, response);
          return;
        }

        // 6b) Enforce token-version to support logout/rotation (server-side revocation).
        int currentVersion = aud.getTokenVersion();
        if (currentVersion != tokenVersionInJwt) {
          SecurityContextHolder.clearContext();
          filterChain.doFilter(request, response);
          return;
        }
      }

      // 7) All checks passed → create an authenticated token with authorities.
      UsernamePasswordAuthenticationToken authToken =
          new UsernamePasswordAuthenticationToken(userDetails, null, userDetails.getAuthorities());
      authToken.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
      SecurityContextHolder.getContext().setAuthentication(authToken);
    }

    // 8) Always continue the chain (either authenticated or anonymous).
    filterChain.doFilter(request, response);
  }
}
