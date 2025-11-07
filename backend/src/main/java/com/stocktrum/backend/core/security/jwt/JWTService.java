// Handles token generation and claim extraction.

package com.stocktrum.backend.core.security.jwt;

import com.stocktrum.backend.features.user.domain.User;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.io.Decoders;
import io.jsonwebtoken.security.Keys;
import org.springframework.stereotype.Service;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.util.Base64;
import java.util.Date;

@Service
public class JWTService {
  private String secretKey = "";

  public JWTService() {
    try {
      KeyGenerator keyGen = KeyGenerator.getInstance("HmacSHA256");
      SecretKey sk = keyGen.generateKey();
      secretKey = Base64.getEncoder().encodeToString(sk.getEncoded());
    } catch (NoSuchAlgorithmException e) {
      throw new RuntimeException("Failed to initialize JWTService: " + e.getMessage());
    }
  }

  public String generateAccessToken(User user) {
    return Jwts.builder()
        .subject(user.getUserId().toString())
        .issuedAt(Date.from(Instant.now()))
        .expiration(
            Date.from(Instant.now().plusSeconds(15 * 60)))
        .claim("tv", user.getTokenVersion())
        .claim("uname", user.getEmail())
        .signWith(getKey())
        .compact();
  }

  private SecretKey getKey() {
    byte[] keyBytes = Decoders.BASE64.decode(secretKey);
    return Keys.hmacShaKeyFor(keyBytes);
  }

  // Verify signature + expiration, then return claims
  public Claims parseAndValidate(String token) {
    return Jwts.parser().verifyWith(getKey()).build().parseSignedClaims(token).getPayload();
  }
}
